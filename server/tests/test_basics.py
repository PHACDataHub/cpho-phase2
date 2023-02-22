import json

from graphene_django.utils.testing import GraphQLTestCase, TestCase


class HelloWorldTestCase(GraphQLTestCase):
    def test_basic_connectivity(self):
        print("* test_basic_connectivity")
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
        print("* test_no_errors_occur_when_asking_for_schema_details")
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
