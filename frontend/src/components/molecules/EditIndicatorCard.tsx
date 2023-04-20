import { useQuery } from "@apollo/client";
import { Box, Heading, Spinner, Text } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { GET_INDICATOR_DATA } from "../../utils/graphql/queries";
import { IndicatorType } from "../../utils/types";

const EditIndicatorCard = ({ id }: { id: number }) => {
  const { loading, error, data } = useQuery<{ indicator: IndicatorType }>(
    GET_INDICATOR_DATA,
    {
      variables: { id: Number(id) },
      fetchPolicy: "network-only",
    }
  );

  const indicator = data?.indicator;

  const navigate = useNavigate();

  if (loading) return <Spinner />;

  if (error) return <Text>Error loading indicator with id {id}</Text>;

  return (
    <Box
      bgColor="gray.200"
      _dark={{
        bgColor: "gray.600",
      }}
      py={2}
      px={4}
      borderRadius="lg"
      cursor="pointer"
      scale={0}
      _hover={{
        scale: 1.05,
      }}
      onClick={() => navigate(`/modify-indicator/${id}`)}
    >
      <Heading size="md">{data?.indicator.name}</Heading>
      <Heading size="sm" fontWeight="normal" fontStyle="italic">
        {indicator?.indicatordataSet.length} data point
        {indicator?.indicatordataSet.length === 1 ? "" : "s"}
      </Heading>
    </Box>
  );
};

export default EditIndicatorCard;
