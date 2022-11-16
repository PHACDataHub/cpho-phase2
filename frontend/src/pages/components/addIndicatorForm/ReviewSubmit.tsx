import { useMutation } from "@apollo/client";
import { Button, Heading, VStack } from "@chakra-ui/react";
import { categories, sub_categories } from "../../../utils/constants";
import { CREATE_INDICATOR } from "../../../utils/graphql/mutations";
import {
  GET_INDICATOR_OVERVIEW,
  GET_INDICATORS_AND_IDS,
} from "../../../utils/graphql/queries";
import { DataPoint } from "../../../utils/types";

const ReviewSubmit = ({
  values,
}: {
  values: {
    indicatorName: string;
    detailedIndicator: string;
    category: number;
    subCategory: number;
    dataPoints: DataPoint[];
  };
}) => {
  const {
    indicatorName,
    detailedIndicator,
    category,
    subCategory,
    dataPoints,
  } = values;

  const [createIndicator, { loading, error, data }] = useMutation(
    CREATE_INDICATOR,
    {
      refetchQueries: [
        {
          query: GET_INDICATOR_OVERVIEW,
        },
        {
          query: GET_INDICATORS_AND_IDS,
        },
      ],
    }
  );

  return (
    <VStack>
      {loading && <Heading size="md">Loading...</Heading>}
      {error && <Heading size="md">Error: {error.message}</Heading>}
      {data && <Heading size="md">Success!</Heading>}
      <Button
        w="40%"
        disabled={dataPoints.length === 0}
        colorScheme="green"
        onClick={() => {
          createIndicator({
            variables: {
              category: categories.find((c) => c.id === category)?.label ?? "",
              detailedIndicator,
              indicator: indicatorName,
              subIndicatorMeasurement: "",
              topic:
                sub_categories.find((c) => c.id === subCategory)?.label ?? "",
              dataPoints: dataPoints.map((d) => ({
                ...d,
                value: +d.value, // Gets number representation for float values to fix GraphQL query error
                valueLowerBound: +d.valueLowerBound,
                valueUpperBound: +d.valueUpperBound,
              })),
            },
          });
        }}
      >
        Submit
      </Button>
    </VStack>
  );
};

export default ReviewSubmit;
