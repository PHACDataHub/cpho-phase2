import { VStack, Text, Spinner } from "@chakra-ui/react";
import { Page } from "./Page";
import { gql, useQuery } from "@apollo/client";

export function PastSubmissions() {
  const GET_INDICATORS = gql`
    query {
      indicators {
        id
        indicator
      }
    }
  `;

  const { loading, error, data } = useQuery<{
    indicators: {
      id: number;
      indicator: string;
    }[];
  }>(GET_INDICATORS);

  const indicators = data?.indicators;

  return (
    <Page
      title="Past Submissions"
      backButton={{ show: true, redirectUrl: "/" }}
    >
      <VStack>
        {loading && <Spinner />}
        {error && <Text>Error loading indicators</Text>}
        {indicators ? (
          indicators.map(({ id, indicator }) => (
            <Text key={id}>{indicator}</Text>
          ))
        ) : (
          <Spinner />
        )}
      </VStack>
    </Page>
  );
}
