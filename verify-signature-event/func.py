#
# oci-verify-signature-event
#
# Copyright (c) 2020 Oracle, Inc.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

import io
import os
import json
import sys
import hashlib
import base64
import logging

from fdk import response

import oci.object_storage

# Get destination namespace, bucket from function config
# Get Object OCID from event
# Get signature from object itself (metadata)
# Calculate message digest from object itself
# Verify signature - if verified, write to Verified bucket
#  
def handler(ctx, data: io.BytesIO=None):
    try:    
        # Verify Flag
        # Will be set to true if verified
        verified = False

        # From function configuration
        cfg = dict(ctx.Config())
        destination_bucket = cfg["destination_bucket"]
        destination_ns = cfg["destination_namespace"]
        endpoint = cfg["endpoint"]
        key_ocid = cfg["key_ocid"]
        key_version_ocid = cfg["key_version_ocid"]
        signing_algorithm = cfg["signing_algorithm"]
        logging.getLogger().info("Key Version OCID = " + key_version_ocid)
        logging.getLogger().info("Key OCID = " + key_ocid)
        logging.getLogger().info("Signing Algorithm = " + signing_algorithm)
        logging.getLogger().info("Crypto Endpoint = " + endpoint)
        logging.getLogger().info("Destination Namespace = " + destination_ns)
        logging.getLogger().info("Destination Bucket = " + destination_bucket)

        # Get details from event
        event = json.loads(data.getvalue())
        event_data = event.get("data")
        bucket_name = event_data.get("additionalDetails").get("bucketName")
        object_name = event_data.get("resourceName")
        logging.getLogger().info("Event Bucket: " + bucket_name)
        logging.getLogger().info("Event Object Name: " + object_name)

        # Get reference to OCI
        signer = oci.auth.signers.get_resource_principals_signer()
        object_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
        crypto_client = oci.key_management.KmsCryptoClient(config={}, signer=signer, service_endpoint=endpoint)

        # Grab actual message
        namespace = object_client.get_namespace().data
        object = get_object(object_client, namespace, bucket_name,object_name)


        # Get Actual object for signature verify
        digest = get_digest_from_message(object)
        object_headers = object.headers
        signature = object_headers.get("opc-meta-signature")
        logging.getLogger().info("Signature: " + signature)
        logging.getLogger().info("Digest: " + digest)

        # Verify signature
        verify_response = crypto_client.verify(
            verify_data_details=oci.key_management.models.VerifyDataDetails(
                key_id=key_ocid,
                key_version_id=key_version_ocid,
                signature=signature,
                message=digest,
                signing_algorithm=signing_algorithm,
                message_type="DIGEST")
        )
        logging.getLogger().info(verify_response.data)
        verify_response_json = json.loads(str(verify_response.data))
        verified = bool(verify_response_json.get("is_signature_valid"))
        if (verified):
            # Place on new bucket
            object_client.put_object(destination_ns,destination_bucket,object_name,str.encode(object.data.text),opc_meta={"verified":True})
            logging.getLogger().info("Wrote to bucket")
            return None
        else:
            logging.getLogger().info("Doing nothing - not verified")
        crypto_client
    except Exception as ex:
        logging.getLogger().error("Error: " + str(ex))
        return None
########################################### 
# Helper methods
def get_object(client, namespace, bucketName, objectName):
    try:
        print("Searching for bucket and object", flush=True)
        object = client.get_object(namespace, bucketName, objectName)
        print("found object", flush=True)
        if object.status == 200:
            #print("Success: The object " + objectName + " was retrieved with the content: " + object.data.text, flush=True)
            return object

            # Place on another bucket
            client.put_object(bucket_ns,verified_bucket,objectName,object.data,opc_meta={"verified":True})
        else:
            message = "Failed: The object " + objectName + " could not be retrieved."
    except Exception as e:
        return None

def get_digest_from_message(object):
    m = hashlib.sha224()
    m.update(str.encode(object.data.text))
    digest = base64.b64encode(m.digest()).decode()
    return digest
