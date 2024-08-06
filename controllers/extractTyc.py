from datetime import datetime
import logging
from os import getenv
import asyncio
import json
from typing import NoReturn
from google.cloud import pubsub_v1
from google.pubsub_v1.types import PullRequest
from google.oauth2 import service_account
import google.api_core.exceptions
from services.in_memory_cache import add_message, is_message_processed
from services.storage import download_file
from services.alloyDB import execute_bulk_query
import hashlib

subscriber = None
subscription_path = None

project_id = getenv("GCP_PROJECT_ID")
subscription_id = getenv("SUBSCRIPTION_ID")
max_messages = int(getenv("MAX_MESSAGES", 1))
credentials_path = getenv("GCP_CREDENTIALS")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def initialize_pubsub_service() -> None:
    global subscriber, subscription_path
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )
    subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    asyncio.create_task(listen_for_messages())

async def listen_for_messages() -> NoReturn:
    logging.info("Listening for messages...")
    while True:
        try:
            response = subscriber.pull(
                request=PullRequest(
                    subscription=subscription_path,
                    max_messages=max_messages,
                    return_immediately=False,
                ),
                timeout=90,
            )
            if response.received_messages:
                ack_ids = []
                for msg in response.received_messages:
                    try:
                        message_data = json.loads(msg.message.data.decode("utf-8"))
                        message_hash = get_message_hash(message_data)
                        logging.info(f"Received message: {msg.message.data.decode('utf-8')}")
                        logging.info(f"message_hash: {message_hash}")
                        
                        if await is_message_processed(message_hash):
                            logging.info(f"Already processed message_hash: {message_hash}")
                            ack_ids.append(msg.ack_id)
                            continue
                        
                        await add_message(message_hash)
                        event_type = msg.message.attributes.get("eventType")
                        logging.info(f"event_type: {event_type}")
                        
                        if event_type == "OBJECT_FINALIZE":
                            logging.info(f"Received message: {message_data}")
                            ack_ids.append(msg.ack_id)
                            
                            file_name = message_data.get("name")
                            if file_name:
                                logging.info(f"File name: {file_name}")
                                file_content = download_file(file_name)
                                if file_content:
                                    logging.info("File content downloaded successfully")
                                    file_data = json.loads(file_content.decode('utf-8'))
                                    if isinstance(file_data, dict):
                                        file_data = [file_data]  # Convert to list if it's a single record
                                    
                                    check_values = []
                                    insert_values = []
                                    for record in file_data:
                                        payload = record.get("payload", {})
                                        
                                        # Convert date strings to datetime objects
                                        atmfromdatetime = datetime.strptime(payload.get("atmfromdatetime"), "%Y-%m-%d %H:%M:%S.%f")
                                        atmtodatetime = datetime.strptime(payload.get("atmtodatetime"), "%Y-%m-%d %H:%M:%S.%f")
                                        
                                        check_values.append((
                                            payload.get("atmidentifier"),
                                            payload.get("atmaddress_streetname"),
                                            payload.get("atmaddress_buildingnumber"),
                                            payload.get("atmtownname"),
                                            payload.get("atmdistrictname"),
                                            payload.get("atmcountrysubdivisionmajorname")
                                        ))
                                        
                                        insert_values.append((
                                            payload.get("atmidentifier"),
                                            payload.get("atmaddress_streetname"),
                                            payload.get("atmaddress_buildingnumber"),
                                            payload.get("atmtownname"),
                                            payload.get("atmdistrictname"),
                                            payload.get("atmcountrysubdivisionmajorname"),
                                            atmfromdatetime,
                                            atmtodatetime,
                                            payload.get("atmtimetype"),
                                            payload.get("atmattentionhour"),
                                            payload.get("atmservicetype"),
                                            payload.get("atmaccesstype")
                                        ))
                                    
                                    # Check for existing records
                                    check_query = """
                                        SELECT id, atmidentifier, atmaddress_streetname, atmaddress_buildingnumber,
                                               atmtownname, atmdistrictname, atmcountrysubdivisionmajorname
                                        FROM presential_service_channels.automated_teller_machines
                                        WHERE (atmidentifier, atmaddress_streetname, atmaddress_buildingnumber,
                                               atmtownname, atmdistrictname, atmcountrysubdivisionmajorname) = ($1, $2, $3, $4, $5, $6)
                                    """
                                    existing_records = await execute_bulk_query(check_query, check_values)
                                    
                                    # Prepare update and insert lists
                                    update_values = []
                                    new_insert_values = []
                                    
                                    if existing_records is not None:
                                        for i, record in enumerate(insert_values):
                                            matching_record = next((er for er in existing_records if er[1:] == check_values[i]), None)
                                            if matching_record:
                                                update_values.append((
                                                    record[6],  # atmfromdatetime
                                                    record[7],  # atmtodatetime
                                                    record[8],  # atmtimetype
                                                    record[9],  # atmattentionhour
                                                    record[10], # atmservicetype
                                                    record[11], # atmaccesstype
                                                    matching_record[0]  # id
                                                ))
                                            else:
                                                new_insert_values.append(record)
                                    else:
                                        logging.warning("No existing records found or query returned None. Proceeding with insert for all records.")
                                        new_insert_values = insert_values
                                    
                                    # Perform updates
                                    if update_values:
                                        update_query = """
                                            UPDATE presential_service_channels.automated_teller_machines
                                            SET atmfromdatetime = $1,
                                                atmtodatetime = $2,
                                                atmtimetype = $3,
                                                atmattentionhour = $4,
                                                atmservicetype = $5,
                                                atmaccesstype = $6
                                            WHERE id = $7
                                        """
                                        update_result = await execute_bulk_query(update_query, update_values)
                                        logging.info(f"Updated {update_result} records")
                                    
                                    # Perform inserts
                                    if new_insert_values:
                                        insert_query = """
                                            INSERT INTO presential_service_channels.automated_teller_machines (
                                                atmidentifier, atmaddress_streetname, atmaddress_buildingnumber,
                                                atmtownname, atmdistrictname, atmcountrysubdivisionmajorname,
                                                atmfromdatetime, atmtodatetime, atmtimetype,
                                                atmattentionhour, atmservicetype, atmaccesstype
                                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                                        """
                                        insert_result = await execute_bulk_query(insert_query, new_insert_values)
                                        logging.info(f"Inserted {insert_result} new records")
                                else:
                                    logging.error(f"Failed to download file content for {file_name}")
                            else:
                                logging.warning("No file name found in the message")
                        else:
                            logging.info(f"Ignoring message with event type: {event_type}")
                    
                    except json.JSONDecodeError as json_err:
                        logging.error(f"Error decoding JSON: {str(json_err)}")
                    except ValueError as ve:
                        logging.error(f"Error parsing datetime: {str(ve)}")
                    except Exception as e:
                        logging.error(f"Error processing message: {str(e)}")
                    
                if ack_ids:
                    subscriber.acknowledge(
                        request={"subscription": subscription_path, "ack_ids": ack_ids}
                    )
        except google.api_core.exceptions.DeadlineExceeded:
            logging.warning("DeadlineExceeded: Pull request timed out, retrying...")
        except Exception as e:
            logging.error(f"Unexpected error in listen_for_messages: {str(e)}")
        
        await asyncio.sleep(1)

def get_message_hash(message_data: dict) -> str:
    message_str = json.dumps(message_data, sort_keys=True)
    return hashlib.sha256(message_str.encode("utf-8")).hexdigest()