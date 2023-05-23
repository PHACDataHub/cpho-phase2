import json

import pytest
from graphene_django.utils.testing import GraphQLTestCase, TestCase


@pytest.skip("TODO: convert to pytest", allow_module_level=True)
class HelloWorldTestCase(GraphQLTestCase):
    def test_basic_connectivity(self):
        response = self.query(
            """
            query {
               __schema {
                 queryType {
                   name
                 }
               }
             }
            """,
        )

        content = json.loads(response.content)
        self.assertEqual(
            content, {"data": {"__schema": {"queryType": {"name": "Query"}}}}
        )

    def test_no_errors_occur_when_asking_for_schema_details(self):
        response = self.query(
            """
            query {
               __schema {
                 queryType {
                   name
                 }
               }
             }
            """,
        )

        self.assertResponseNoErrors(response)
