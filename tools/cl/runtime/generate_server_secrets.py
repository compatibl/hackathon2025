# Copyright (C) 2023-present The Project Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import secrets
import uuid
from pathlib import Path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cl.runtime.secret_providers.secret_provider import SecretProvider
from cl.runtime.serializers.bootstrap_serializers import BootstrapSerializers
from cl.runtime.settings.project_settings import ProjectSettings


def _generate_rsa_private_cert() -> str:
    # Generate private key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    # Convert private key to PEM format
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    # Convert PEM bytes to string
    pem_str = pem.decode("utf-8")
    return pem_str


SECRETS_FILE_NAME = ".secrets.yaml"
SECRETS = {
    "AUTH-TOKEN-KEY": {
        "secret_type": "dynamic",
        "content_type": "password",
        "func": lambda: secrets.token_urlsafe(64),
    },
    "OKTA-CLIENT-SECRET": {
        "secret_type": "static",
        "content_type": "password",
        "func": lambda: os.getenv("OKTA_CLIENT_SECRET"),
    },
    "KINDE-CLIENT-SECRET": {
        "secret_type": "static",
        "content_type": "password",
        "func": lambda: os.getenv("KINDE_CLIENT_SECRET"),
    },
    "USER-SECRETS-PRIVATE-CERT": {
        "secret_type": "dynamic",
        "content_type": "private_rsa",
        "func": _generate_rsa_private_cert,
    },
}


class SecretsGenerator:

    @classmethod
    def run(cls, mode: str) -> None:
        """Generate new server secrets to yaml file at predefined path."""
        provider = SecretProvider.create()
        if mode == "recreate":
            raise RuntimeError("Recreate mode is not supported when running on localhost.")  # TODO: !!! To avoid merge errors, avoid differences between dev and enterprise code here

        for secret_title, secret_data in SECRETS.items():
            try:
                secret_value = provider.get_secret(secret_title)
            except Exception:
                secret_value = None
            if mode == "keep" and secret_value is not None:
                print(f"Mode: {mode} -> {secret_title} already exists, skip...")
                continue
            if secret_value and secret_data["secret_type"] == "static":
                print(f"Mode: {mode} -> {secret_title} already exists and dont have dynamic value, skip...")
                continue

            if secret_value := secret_data["func"]():
                print(f"Mode: {mode} -> {secret_title} add new version")
                provider.add_secret(secret_title, secret_value)
            else:
                print(f"Cant get value for {secret_title}. Check secret generation instruction")



if __name__ == '__main__':
    import argparse


    def parse_args():
        parser = argparse.ArgumentParser(
            description="Run text generation with specified model and prompt."
        )

        parser.add_argument(
            "--mode", "-m",
            type=str,
            default="keep",
            choices=["keep", "recreate", "add"],
            help="Secret generation mode:\n"
                 "keep - do not touch secrets that exists, add new secrets\n"
                 "recreate - remove old secrets, write new (only for local)\n"
                 "add - create new secrets, update versions of secrets that already exists\n"
        )

        return parser.parse_args()
    args = parse_args()
    SecretsGenerator.run(mode=args.mode)
