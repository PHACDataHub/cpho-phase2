import { VStack, Text, Spinner, Center } from "@chakra-ui/react";
import { Page } from "../template/Page";
import { useQuery } from "@apollo/client";
import { GET_INDICATORS_AND_IDS } from "../../utils/graphql/queries";
import EditIndicatorCard from "../molecules/EditIndicatorCard";

export function ModifyPastSubmissions() {
  const { loading, error, data } = useQuery<{
    indicators: {
      id: number;
      indicator: string;
    }[];
  }>(GET_INDICATORS_AND_IDS);

  const indicators = data?.indicators;

  return (
    <Page
      title="Past Submissions"
      backButton={{ show: true, redirectUrl: "/" }}
    >
      <Center>
        <VStack
          justify="center"
          align="stretch"
          maxW={["100%", "90%", "80%", "70%"]}
        >
          {loading && <Spinner />}
          {error && <Text>Error loading indicators</Text>}
          {!loading && indicators && indicators?.length > 0 ? (
            indicators?.map(({ id }) => <EditIndicatorCard key={id} id={id} />)
          ) : (
            <Text>No indicators found</Text>
          )}
        </VStack>
      </Center>
    </Page>
  );
}
