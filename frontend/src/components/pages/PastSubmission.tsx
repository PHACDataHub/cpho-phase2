import { VStack, Text, Spinner } from "@chakra-ui/react";
import { Page } from "../template/Page";
import { useQuery } from "@apollo/client";
import { GET_INDICATORS_AND_IDS } from "../../utils/graphql/queries";
import PastIndicatorBox from "../molecules/PastIndicatorBox";

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
        {indicators && indicators?.length > 0 ? (
          indicators?.map(({ id, indicator }) => <PastIndicatorBox id={id} />)
        ) : (
          <Text>No indicators found</Text>
        )}
      </VStack>
    </Page>
  );
}
