import { useMutation } from "@apollo/client";
import {
  Button,
  Heading,
  HStack,
  StatDownArrow,
  VStack,
} from "@chakra-ui/react";
import { useState } from "react";
import { MODIFY_INDICATOR } from "../../utils/graphql/mutations";
import { IndicatorType } from "../../utils/types";
import DataPointDisplay from "../organisms/DataPointDisplay";

const UpdateSubmit = ({ values }: { values: IndicatorType }) => {
  const {
    id,
    name: indicatorName,
    detailedIndicator,
    category,
    subCategory,
    indicatordataSet: dataPoints,
  } = values;

  const [modifyIndicator, { loading, error, data }] =
    useMutation(MODIFY_INDICATOR);

  const [openTable, setOpenTable] = useState(false);

  return (
    <VStack align="start" spacing={8} w={["98%", "80%", "70%"]}>
      <Heading alignSelf="center">Review and Submit</Heading>

      <HStack spacing={6}>
        <Heading size="lg">
          You are updating{" "}
          <Heading as="span" size="lg" color="blue.500">
            {indicatorName
              ? ` ${indicatorName}`
              : " NULL - INDICATOR NOT SELECTED"}
          </Heading>{" "}
          with{" "}
          <Heading as="span" color="blue.500" size="lg">
            {dataPoints.length}
          </Heading>{" "}
          data point{dataPoints.length === 1 ? "" : "s"}
        </Heading>
        <Button
          leftIcon={
            <StatDownArrow
              color={openTable ? "red.500" : "green.500"}
              transform={openTable ? "rotate(180deg)" : "rotate(0deg)"}
            />
          }
          onClick={() => setOpenTable(!openTable)}
        >
          Review Data
        </Button>
      </HStack>

      {openTable && <DataPointDisplay dataPoints={dataPoints} />}

      <VStack align="start">
        <Heading fontSize="x-large">
          Category:{" "}
          <Heading fontSize="x-large" as="span" color="blue.500">
            {category}
          </Heading>
        </Heading>
        <Heading fontSize="x-large">
          Subcategory:{" "}
          <Heading fontSize="x-large" as="span" color="blue.500">
            {subCategory}
          </Heading>
        </Heading>
        <Heading fontSize="x-large">
          Detailed Indicator:{" "}
          <Heading fontSize="x-large" as="span" color="blue.500">
            {detailedIndicator}
          </Heading>
        </Heading>
      </VStack>

      {loading && <Heading size="md">Loading...</Heading>}
      {error && <Heading size="md">Error: {error.message}</Heading>}
      {data && <Heading size="md">Success!</Heading>}
      {!data && !error && (
        <Button
          alignSelf="end"
          disabled={dataPoints.length === 0}
          colorScheme="green"
          isDisabled={loading}
          onClick={() => {
            modifyIndicator({
              variables: {
                id: Number(id),
                category: category,
                detailedIndicator,
                name: indicatorName,
                subIndicatorMeasurement: "",
                subCategory,
                dataPoints: dataPoints.map(({ id, indicatorId, ...d }) => ({
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
          Update Indicator
        </Button>
      )}
    </VStack>
  );
};

export default UpdateSubmit;
