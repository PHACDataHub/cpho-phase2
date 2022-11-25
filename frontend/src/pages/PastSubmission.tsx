import { VStack, Text, Spinner } from "@chakra-ui/react";
import { Page } from "./Page";
import { useQuery } from "@apollo/client";
import { GET_INDICATORS_AND_IDS } from "../utils/graphql/queries";

export function PastSubmissions() {
  const { loading, error, data } = useQuery<{
    indicators: {
      id: number;
      indicator: string;
    }[];
  }>(GET_INDICATORS_AND_IDS, {
    fetchPolicy: "network-only",
  });

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
