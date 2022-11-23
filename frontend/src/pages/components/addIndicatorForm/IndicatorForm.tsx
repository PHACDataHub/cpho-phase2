import { VStack, Button, ButtonGroup, Box } from "@chakra-ui/react";
import { useState } from "react";
import { DataPoint } from "../../../utils/types";
import { AddDataPointButton } from "../AddDataPointButton";
import { DataPointContainer } from "../DataPointContainer";
import IndicatorGenInfo from "./IndicatorGenInfo";
import ReviewSubmit from "./ReviewSubmit";

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

  const [step, setStep] = useState(1);

  const nextStep = () => step < 3 && setStep(step + 1);
  const prevStep = () => step > 1 && setStep(step - 1);

  return (
    <VStack w="100%">
      <ButtonGroup py={4}>
        <Button disabled={step <= 1} onClick={prevStep}>
          Previous
        </Button>
        <Button disabled={step >= 3 || indicatorName === ""} onClick={nextStep}>
          Next
        </Button>
      </ButtonGroup>

      {step === 1 && (
        <Box>
          <IndicatorGenInfo
            indicatorName={indicatorName}
            detailedIndicator={detailedIndicator}
            category={category}
            subCategory={subCategory}
            setField={setField}
          />
        </Box>
      )}
      {step === 2 && (
        <VStack w="100%">
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
      {step === 3 && <ReviewSubmit values={values} />}
    </VStack>
  );
};

export default IndicatorForm;
