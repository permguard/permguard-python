# Copyright 2025 Nitro Agility S.r.l.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import json

from permguard_sdk.az.azreq.builder_action import ActionBuilder
from permguard_sdk.az.azreq.builder_context import ContextBuilder
from permguard_sdk.az.azreq.builder_evaluation import EvaluationBuilder
from permguard_sdk.az.azreq.builder_principal import PrincipalBuilder
from permguard_sdk.az.azreq.builder_request_atomic import AZAtomicRequestBuilder
from permguard_sdk.az.azreq.builder_request_composed import AZRequestBuilder
from permguard_sdk.az.azreq.builder_resource import ResourceBuilder
from permguard_sdk.az.azreq.builder_subject import SubjectBuilder
from permguard_sdk.az.azreq.model import AZRequest
from permguard_sdk.az_client import AZClient
from permguard_sdk.az_config import with_endpoint


# Caricamento del file JSON incorporato (equivalente a `//go:embed`)
with open("./examples/cmd/requests/ok_onlyone1.json", "r") as f:
    json_file = f.read()


def check_json_request():
    """Check an authorization request from a JSON file."""
    az_client = AZClient(with_endpoint("localhost", 9094))

    try:
        # Deserializza la richiesta JSON in un oggetto AZRequest
        req = AZRequest.model_validate_json(json_file)
    except json.JSONDecodeError:
        print("❌ Authorization request deserialization failed")
        return

    # Effettua la verifica di autorizzazione
    decision, response, _ = az_client.check(req)
    print_authorization_result(decision, response)


def check_atomic_evaluation():
    """Check an atomic authorization evaluation."""
    az_client = AZClient(with_endpoint("localhost", 9094))

    # Creazione del Principal
    principal = PrincipalBuilder("amy.smith@acmecorp.com").build()

    # Creazione delle entità
    entities = [
        {
            "uid": {"type": "MagicFarmacia::Platform::BranchInfo", "id": "subscription"},
            "attrs": {"active": True},
            "parents": [],
        }
    ]

    # Creazione della richiesta di autorizzazione
    req = (
        AZAtomicRequestBuilder(
            895741663247,
            "809257ed202e40cab7e958218eecad20",
            "platform-creator",
            "MagicFarmacia::Platform::Subscription",
            "MagicFarmacia::Platform::Action::create",
        )
        .with_request_id("1234")
        .with_principal(principal)
        .with_entities_items("cedar", entities)
        .with_subject_role_actor_type()
        .with_subject_source("keycloack")
        .with_subject_property("isSuperUser", True)
        .with_resource_id("e3a786fd07e24bfa95ba4341d3695ae8")
        .with_resource_property("isEnabled", True)
        .with_action_property("isEnabled", True)
        .with_context_property("time", "2025-01-23T16:17:46+00:00")
        .with_context_property("isSubscriptionActive", True)
        .build()
    )

    # Effettua la verifica di autorizzazione
    decision, response, _ = az_client.check(req)
    print_authorization_result(decision, response)


def check_multiple_evaluations():
    """Check multiple authorization evaluations."""
    az_client = AZClient(with_endpoint("localhost", 9094))

    # Creazione del Subject
    subject = (
        SubjectBuilder("platform-creator")
        .with_role_actor_type()
        .with_source("keycloack")
        .with_property("isSuperUser", True)
        .build()
    )

    # Creazione della Risorsa
    resource = (
        ResourceBuilder("MagicFarmacia::Platform::Subscription")
        .with_id("e3a786fd07e24bfa95ba4341d3695ae8")
        .with_property("isEnabled", True)
        .build()
    )

    # Creazione delle Azioni
    action_view = ActionBuilder("MagicFarmacia::Platform::Action::view").with_property("isEnabled", True).build()
    action_create = ActionBuilder("MagicFarmacia::Platform::Action::create").with_property("isEnabled", True).build()

    # Creazione del Context
    context = (
        ContextBuilder()
        .with_property("time", "2025-01-23T16:17:46+00:00")
        .with_property("isSubscriptionActive", True)
        .build()
    )

    # Creazione delle Valutazioni
    evaluation_view = EvaluationBuilder(subject, resource, action_view).with_request_id("1234").with_context(context).build()
    evaluation_create = EvaluationBuilder(subject, resource, action_create).with_request_id("7890").with_context(context).build()

    # Creazione del Principal
    principal = PrincipalBuilder("amy.smith@acmecorp.com").build()

    # Creazione delle entità
    entities = [
        {
            "uid": {"type": "MagicFarmacia::Platform::BranchInfo", "id": "subscription"},
            "attrs": {"active": True},
            "parents": [],
        }
    ]

    # Creazione della richiesta di autorizzazione
    req = (
        AZRequestBuilder(895741663247, "809257ed202e40cab7e958218eecad20")
        .with_principal(principal)
        .with_entities_items("cedar", entities)
        .with_evaluation(evaluation_view)
        .with_evaluation(evaluation_create)
        .build()
    )

    # Effettua la verifica di autorizzazione
    decision, response, _ = az_client.check(req)
    print_authorization_result(decision, response)


def print_authorization_result(decision, response):
    """Print the result of an authorization request."""
    if decision:
        print("✅ Authorization Permitted")
    else:
        print("❌ Authorization Denied")
        if response and response.context:
            if response.context.reason_admin:
                print(f"-> Reason Admin: {response.context.reason_admin.message}")
            if response.context.reason_user:
                print(f"-> Reason User: {response.context.reason_user.message}")
            for eval in response.evaluations:
                if eval.context and eval.context.reason_user:
                    print(f"-> Reason Admin: {eval.context.reason_admin.message}")
                    print(f"-> Reason User: {eval.context.reason_user.message}")


# Esegui i test
if __name__ == "__main__":
    #check_json_request()
    check_atomic_evaluation()
    #check_multiple_evaluations()
