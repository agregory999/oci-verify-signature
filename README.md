# Digital Signature Verification

This use case is based on a customer requirement to ensure that messages received as part of a processing flow are verified to have been untouched since they were created.  The original example uses XML Digital Signature in Java, and is implemented as an Oracle Service Bus callout.  As part of a move to Oracle Integration Cloud (OIC), the same type of flow is needed, but without a Java callout.   

This repository contains functions written to accomplish the task of taking an XML file, along with the OCID of a pre-shared secret key, doign the validation, and returning `true` or `false`.  

Each function can stand on its own, but likely is to be incorporated into a processing flow.  Included are call examples and the overall flow if applicable.  

- [Python - Message Signing](sign-message-python) 
- [Python - Signature Verification](verify-signature-python) 
- [Event Flow - Python](verify-signature-python-event) 
- [XML Digital Signature - Java](verify-signature-java) 
 
