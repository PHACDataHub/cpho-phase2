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
      <Heading>Review and Submit</Heading>
      {indicatorName ? (
        <Heading size="lg">
          You are adding{" "}
          <Heading as="span" color="blue.500" size="lg">
            {dataPoints.length}
          </Heading>{" "}
          data point{dataPoints.length === 1 ? "" : "s"} to
          <Heading as="span" size="lg" color="blue.500">
            {` ${indicatorName}`}
          </Heading>
        </Heading>
      ) : (
        <Heading size="lg">
          Please select an indicator in the first step
        </Heading>
      )}
      <Heading size="lg">
        Category:{" "}
        <Heading size="lg" as="span" color="blue.500">
          {categories.filter((c) => c.id === category)[0].label}
        </Heading>
      </Heading>
      <Heading size="lg">
        Subcategory:{" "}
        <Heading size="lg" as="span" color="blue.500">
          {sub_categories.filter((c) => c.id === subCategory)[0].label}
        </Heading>
      </Heading>
      {loading && <Heading size="md">Loading...</Heading>}
      {error && <Heading size="md">Error: {error.message}</Heading>}
      {data && <Heading size="md">Success!</Heading>}
      {!data && !error && (
        <Button
          disabled={dataPoints.length === 0}
          colorScheme="green"
          isDisabled={loading}
          onClick={() => {
            createIndicator({
              variables: {
                category:
                  categories.find((c) => c.id === category)?.label ?? "",
                detailedIndicator,
                indicator: indicatorName,
                subIndicatorMeasurement: "",
                topic:
                  sub_categories.find((c) => c.id === subCategory)?.label ?? "",
                dataPoints: dataPoints.map(({ uuid, ...d }) => ({
                  ...d,
                  singleYearTimeframe: `${d.singleYearTimeframe}`,
                  multiYearTimeframe: d.multiYearTimeframe
                    ? `${d.multiYearTimeframe![0]}-${d.multiYearTimeframe![1]}`
                    : undefined,
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
      )}
    </VStack>
  );
};

export default ReviewSubmit;
