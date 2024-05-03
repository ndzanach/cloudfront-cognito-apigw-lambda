import time
import json
from jose import jwk, jwt, JWTError
from jose.utils import base64url_decode
import urllib.parse
import urllib.request

AWS_REGION = "YOUR_AWS_REGION"
COGNITO_USER_POOL_ID = "YOUR_COGNITO_USER_POOL_ID"

keys_url = "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
    AWS_REGION, COGNITO_USER_POOL_ID
)

with urllib.request.urlopen(keys_url) as f:
    response = f.read()
    keys = json.loads(response.decode("utf-8"))["keys"]
    print(keys)


class AuthMethod:
    def __init__(self):
        pass

    def verify_token(self, access_token):
        try:
            # get the kid from the headers prior to verification
            headers = jwt.get_unverified_headers(access_token)
            kid = headers["kid"]
            # search for the kid in the downloaded public keys
            key_index = -1
            for i in range(len(keys)):
                if kid == keys[i]["kid"]:
                    key_index = i
                    break
            if key_index == -1:
                print("Public key not found in jwks.json")
                return "deny"
                # raise credentials_exception
            # construct the public key
            public_key = jwk.construct(keys[key_index])
            # get the last two sections of the token,
            # message and signature (encoded in base64)
            message, encoded_signature = str(access_token).rsplit(".", 1)
            # decode the signature
            decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
            # verify the signature
            if not public_key.verify(message.encode("utf8"), decoded_signature):
                print("Signature verification failed")
                return "deny"
                # raise credentials_exception
            print("Signature successfully verified")
            # since we passed the verification, we can now safely
            # use the unverified claims
            claims = jwt.get_unverified_claims(access_token)
            print(claims)
            # additionally we can verify the token expiration
            if time.time() > claims["exp"]:
                print("Token is expired")
                return "deny"
                # raise credentials_exception

            # and the Audience  (use claims['client_id'] if verifying an access token)
            print(claims["client_id"])
            if claims["client_id"] != self.client_id:
                print("Token was not issued for this audience")
                return "deny"
                # raise credentials_exception
            # now we can use the claims
            print(claims)
            return "allow"
        except JWTError:
            return "unauthorized"


class QueryMethod:
    def __init__(self):
        pass
