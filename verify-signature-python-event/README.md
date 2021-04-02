# Digital Signature Verification (Python)

In this flow, a message (any format) is produced on the client side, and a `Signature` is produced using an OCI CLI call (which could also be a function).  The client takes uploads the original to the object bucket, along with metadata that comprises the `signature` that was produced.  This example uses an object bucket as the upload location, and this bucket fires off an event upon insert or update.  The event action to invoke this function, and the function performs the following:
- Pulls the XML message from the Object Store
- Computes a `message digest` using sha224
- Uses OCI KMS Crypto client to `verify` the `signature` and computed `digest`
- If the signature is valid, gthe XML is placed into a different storage bucket with metadata

### Diagram
![Diagram](../images/DigitalSignatureFlow.svg)

## Client Flow
In order to produce the message digest, the client uses openSSL:
```bash
openssl dgst -binary -sha224 file.xml| openssl enc -base64
WiiYYbUrBmSLvtnY3FM5o/CGgMPNh/TntFvdSA==
```
This message digest is used with the OCI CLI or API is used to produce a signature:
```bash
oci --profile INTEGRATION kms crypto signed-data sign --key-id ocid1.key.oc1.iad.bfqfhkltaaeuk.abuwcljsvls5p2jxws7rgg6rmv6wwhv4d2f3jwpy62moxqkj4zbxtdjdyeva --key-version-id ocid1.keyversion.oc1.iad.bfqfhkltaaeuk.aumtmbmqgsiaa.abuwcljsrsaiwd7zsw4oouaiejiwk3jmahexmyizjkmkdxozxuwtqsauh5yq --message-type DIGEST --message "WiiYYbUrBmSLvtnY3FM5o/CGgMPNh/TntFvdSA==" --signing-algorithm SHA_224_RSA_PKCS_PSS --endpoint https://bfqfhkltaaeuk-crypto.kms.us-ashburn-1.oraclecloud.com
{
  "data": {
    "key-id": "ocid1.key.oc1.iad.bfqfhkltaaeuk.abuwcljsvls5p2jxws7rgg6rmv6wwhv4d2f3jwpy62moxqkj4zbxtdjdyeva",
    "key-version-id": "ocid1.keyversion.oc1.iad.bfqfhkltaaeuk.aumtmbmqgsiaa.abuwcljsrsaiwd7zsw4oouaiejiwk3jmahexmyizjkmkdxozxuwtqsauh5yq",
    "signature": "UESjYkFS1Uvkuy5ESmvwJ47YfJTOzD6PVcDqo35DwXSqWgP3OOC4L+xnGMtJT8qbsws8DC+I63FjkP9b7wPxV+FpjVTXTQYf+SwXvlK7zqWeXBoHjLlo5BcUnCMF+4S6kTcq7RNdh6YcCtODdZ8uncSY/RrenjaqyQrjdnVKvSaS25gkmew5m6scprt6ZakDbKUe/G98TL+KWtmSINlIng0oeJWMTaCYkFXNN8lV04wOfE5uCCXQXjhGuNTanvyig+cRbbfxoORa6nO8+y4ffquQ+kE4hLB5K4pMgridqpEEPBP45r3Kg5vjdGshnCbHuOcIigVUQWKf8JASgCVjZw==",
    "signing-algorithm": "SHA_224_RSA_PKCS_PSS"
  }
}
```
The resulting signature is added to an object storage bucket as metadata - note that the digest is explicly **not** sent, as the function will re-calculate the same hashed message digest that was used to generate the signature, and they must match:
```bash
oci --profile INTEGRATION os object put  --bucket-name DigitalSignatureBucket --file file.xml \
--metadata '{"signature": "UESjYkFS1Uvkuy5ESmvwJ47YfJTOzD6PVcDqo35DwXSqWgP3OOC4L+xnGMtJT8qbsws8DC+I63FjkP9b7wPxV+FpjVTXTQYf+SwXvlK7zqWeXBoHjLlo5BcUnCMF+4S6kTcq7RNdh6YcCtODdZ8uncSY/RrenjaqyQrjdnVKvSaS25gkmew5m6scprt6ZakDbKUe/G98TL+KWtmSINlIng0oeJWMTaCYkFXNN8lV04wOfE5uCCXQXjhGuNTanvyig+cRbbfxoORa6nO8+y4ffquQ+kE4hLB5K4pMgridqpEEPBP45r3Kg5vjdGshnCbHuOcIigVUQWKf8JASgCVjZw=="}'
```

## Configure / Deploy

This example requires a few things to be done to set up.  In order for the function to work after deployment, it must be fed an OCI Event.  It also requires 2 Object Storage buckets, one for incoming message and one for verified messages.  Also, the function must be granted permission (by OCI Policy) to access Object storage and OCI Vault.

### Deploy

steps to deploy

### Function Config

steps to configure

### Object Buckets

steps 

### Event Notification

