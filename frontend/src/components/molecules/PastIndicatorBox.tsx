import { useQuery } from "@apollo/client";
import { Box, Heading, Spinner, Text } from "@chakra-ui/react";
import { GET_INDICATOR_DATA } from "../../utils/graphql/queries";
import { Indicator } from "../../utils/types";

const PastIndicatorBox = ({ id }: { id: number }) => {
  const { loading, error, data } = useQuery<{ indicator: Indicator }>(
    GET_INDICATOR_DATA,
    {
      variables: { id: Number(id) },
    }
  );
  return (
    <Box>
      {loading && <Spinner />}
      {error && <Text>Error loading indicator</Text>}
      <Heading size="md">{data?.indicator.indicator}</Heading>
      {/* <Heading size="sm" fontWeight="normal" fontStyle="italic">
        {dataPoints.length} data point{dataPoints.length === 1 ? "" : "s"}
      </Heading> */}
    </Box>
  );
};

export default PastIndicatorBox;
