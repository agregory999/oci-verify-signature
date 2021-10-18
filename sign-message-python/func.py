import io
import json
import logging
import oci
import hashlib
import base64


from fdk import response
from oci.key_management.models import verified_data
from oci.key_management.models.sign_data_details import SignDataDetails


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
        base64message = jsonrequest.get("base64message")
    except Exception as ex:
        print('ERROR: params JSON example: { "base64message":"xxx=="}', ex, flush=True)
        return response.Response(
            ctx, response_data=json.dumps(
            {"error": 'Please send me JSON like this: { "base64message":"xxx=="}'}),
            headers={"Content-Type": "application/json"}
        )

    # Access the KMS API
    
    try:
        signer = oci.auth.signers.get_resource_principals_signer()
        client = oci.key_management.KmsCryptoClient({}, signer=signer, service_endpoint=endpoint)

        # Make the digest
        digest = get_digest_from_string(base64message)

	    # Sign the message
        sign_response = client.sign(
            sign_data_details=SignDataDetails(
                key_id=key_ocid,
                key_version_id=key_version_ocid,
                signing_algorithm=signing_algorithm,
                message=digest,
                message_type="DIGEST"
            )
        )
	        
        logging.getLogger().info(sign_response.data)
        # Return something
        return response.Response(
            ctx, response_data=sign_response.data,
            headers={"Content-Type": "application/json"}
        )

    except (Exception, ValueError) as ex:
        logging.getLogger().info('Error calling verify: ' + str(ex))
        return response.Response(
            ctx, response_data=ex,
            headers={"Content-Type": "application/json"}
        )

#########   Helper Methods  ########
def get_digest_from_string(input):
    m = hashlib.sha224()
    m.update(str.encode(input))
    digest = base64.b64encode(m.digest()).decode()
    return digest