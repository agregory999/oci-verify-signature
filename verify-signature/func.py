import io
import json
import logging
import oci

from fdk import response
from oci.key_management.models import verified_data


def handler(ctx, data: io.BytesIO = None):
 
    # Define required config
    try:
        cfg = dict(ctx.Config())
        key_ocid = cfg["key_ocid"]
        logging.getLogger().info("Key OCID = " + key_ocid)
        key_version_ocid = cfg["key_version_ocid"]
        logging.getLogger().info("Key Version OCID = " + key_version_ocid)
        signing_algorithm = cfg["signing_algorithm"]
        logging.getLogger().info("Signing Algorithm = " + signing_algorithm)
        endpoint = cfg["endpoint"]
        logging.getLogger().info("Endpoint = " + endpoint)
    except Exception as ex:
        print('ERROR: Missing configuration keys required: key_ocid, key_version_ocid, signing_algorithm, endpoint', ex, flush=True)
        return response.Response(
            ctx, response_data=json.dumps(
                {"error": 'Missing configuration keys required: key_ocid, key_version_ocid, signing_algorithm, endpoint'}),
            headers={"Content-Type": "application/json"}
        )

    # Get Request   
    try:
        jsonrequest = json.loads(data.getvalue())
        digest = jsonrequest.get("digest")
        signature = jsonrequest.get("signature")
    except Exception as ex:
        print('ERROR: params JSON example: { "digest":"xxx","signature":"xxx=="}', ex, flush=True)
        return response.Response(
            ctx, response_data=json.dumps(
            {"error": 'Please send me JSON like this: { "digest":"xxx","signature":"xxx=="}'}),
            headers={"Content-Type": "application/json"}
        )

    # Access the KMS API
    
    try:
        signer = oci.auth.signers.get_resource_principals_signer()
        client = oci.key_management.KmsCryptoClient({}, signer=signer, service_endpoint=endpoint)

        # Send the request to service, some parameters are not required, see API
        verify_response = client.verify(
            verify_data_details=oci.key_management.models.VerifyDataDetails(
                key_id=key_ocid,
                key_version_id=key_version_ocid,
                signature=signature,
                message=digest,
                signing_algorithm=signing_algorithm,
                message_type="DIGEST")
        )
        
        logging.getLogger().info(verify_response.data)
        # Return something
        return response.Response(
            ctx, response_data=verify_response.data,
            headers={"Content-Type": "application/json"}
        )

    except (Exception, ValueError) as ex:
        logging.getLogger().info('Error calling verify: ' + str(ex))
        return response.Response(
            ctx, response_data=ex,
            headers={"Content-Type": "application/json"}
        )
   
    # Return something
    return response.Response(
        ctx, response_data=json.dumps(
            {"message": "must have been some issue calling me - check the logs"}),
        headers={"Content-Type": "application/json"}
    )
