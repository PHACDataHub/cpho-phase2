import { useMutation } from "@apollo/client";
import { VStack, Button, Heading, ButtonGroup } from "@chakra-ui/react";
import { useState } from "react";
import { categories, sub_categories } from "../../../utils/constants";
import { CREATE_INDICATOR } from "../../../utils/graphql/mutations";
import {
  GET_INDICATOR_OVERVIEW,
  GET_INDICATORS_AND_IDS,
} from "../../../utils/graphql/queries";
import { useSmallScreen } from "../../../utils/hooks";
import { DataPoint } from "../../../utils/types";
import { AddDataPointButton } from "../AddDataPointButton";
import { DataPointContainer } from "../DataPointContainer";
import IndicatorGenInfo from "./IndicatorGenInfo";

const IndicatorForm = () => {
  const [values, setValues] = useState({
    indicatorName: "",
    detailedIndicator: "",
    category: 1,
    subCategory: 1,
    dataPoints: [] as DataPoint[],
  });

  const {
    indicatorName,
    detailedIndicator,
    category,
    subCategory,
    dataPoints,
  } = values;

  const setField = (field: string, value: any) => {
    setValues({
      ...values,
      [field]: value,
    });
  };

  const smallScreen = useSmallScreen();

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

  const [step, setStep] = useState(1);

  const nextStep = () => step < 3 && setStep(step + 1);
  const prevStep = () => step > 1 && setStep(step - 1);

  return (
    <VStack flexGrow={1}>
      <ButtonGroup>
        <Button disabled={step <= 1} onClick={prevStep}>
          Previous
        </Button>
        <Button disabled={step >= 3} onClick={nextStep}>
          Next
        </Button>
      </ButtonGroup>

      {step === 1 && (
        <IndicatorGenInfo
          indicatorName={indicatorName}
          detailedIndicator={detailedIndicator}
          category={category}
          subCategory={subCategory}
          setField={setField}
        />
      )}
      {step === 2 && (
        <VStack w={smallScreen ? "90%" : "50%"}>
          <AddDataPointButton
            dataPoints={dataPoints}
            setDataPoints={(d) => setField("dataPoints", d)}
          />
          <DataPointContainer
            setDataPoints={(d) => setField("dataPoints", d)}
            dataPoints={dataPoints}
          />
        </VStack>
      )}
      {step === 3 && (
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
                  category:
                    categories.find((c) => c.id === category)?.label ?? "",
                  detailedIndicator,
                  indicator: indicatorName,
                  subIndicatorMeasurement: "",
                  topic:
                    sub_categories.find((c) => c.id === subCategory)?.label ??
                    "",
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
      )}
    </VStack>
  );
};

export default IndicatorForm;
