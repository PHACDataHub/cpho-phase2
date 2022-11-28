import { AddIcon } from "@chakra-ui/icons";
import { VStack, Button, Box, HStack, Heading } from "@chakra-ui/react";
import { useState } from "react";
import { DataPoint, LocationType } from "../../utils/types";
import { AddDataPointButton } from "../molecules/AddDataPointButton";
import { DataPointTable } from "./DataPointTable";
import IndicatorGenInfo from "../molecules/IndicatorGenInfo";
import ReviewSubmit from "../molecules/ReviewSubmit";
import { v4 as uuidv4 } from "uuid";
import StepController from "../molecules/StepController";

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

  const addBlankDataPoint = () => {
    const dataPoint: DataPoint = {
      uuid: uuidv4(),
      country: "CANADA",
      geography: "COUNTRY",
      sex: "",
      gender: "",
      ageGroup: "",
      ageGroupType: "",
      dataQuality: "ACCEPTABLE",
      value: 0,
      valueLowerBound: 0,
      valueUpperBound: 0,
      valueUnit: "PERCENT",
      singleYearTimeframe: 2022,
    };
    setField("dataPoints", [dataPoint, ...dataPoints]);
  };

  const editDataPoint = (uuid: string, field: string, value: any) => {
    const newDataPoints = dataPoints.map((dataPoint) => {
      if (dataPoint.uuid === uuid) {
        if (field === "geography") {
          const country: LocationType =
            value === "COUNTRY"
              ? "CANADA"
              : value === "REGION"
              ? "ATLANTIC"
              : "AB";

          return {
            ...dataPoint,
            geography: value,
            country,
          };
        } else if (field === "singleYearTimeframe") {
          return {
            ...dataPoint,
            singleYearTimeframe: value,
            multiYearTimeframe: undefined,
          };
        } else if (field === "multiYearTimeframe") {
          return {
            ...dataPoint,
            singleYearTimeframe: undefined,
            multiYearTimeframe: value,
          };
        } else {
          return {
            ...dataPoint,
            [field]: value,
          };
        }
      }
      return dataPoint;
    });
    setField("dataPoints", newDataPoints);
  };

  const replaceDataPoint = (uuid: string, newDataPoint: DataPoint) => {
    const newDataPoints = dataPoints.map((dataPoint) => {
      if (dataPoint.uuid === uuid) {
        return newDataPoint;
      }
      return dataPoint;
    });
    setField("dataPoints", newDataPoints);
  };

  const addDataPoint = (newDataPoint: DataPoint) => {
    setField("dataPoints", [newDataPoint, ...dataPoints]);
  };

  const deleteDataPoint = (uuid: string) => {
    const newDataPoints = dataPoints.filter(
      (dataPoint) => dataPoint.uuid !== uuid
    );
    setField("dataPoints", newDataPoints);
  };

  const duplicateDataPoint = (uuid: string) => {
    const idx = dataPoints.findIndex((dataPoint) => dataPoint.uuid === uuid);
    const dataPoint = dataPoints[idx];
    if (dataPoint) {
      setField(
        "dataPoints",
        dataPoints
          .slice(0, idx + 1)
          .concat({ ...dataPoint, uuid: uuidv4() }, dataPoints.slice(idx + 1))
      );
    }
  };

  return (
    <VStack w="100%">
      <StepController
        step={step}
        setStep={setStep}
        isPrevDisabled={step === 1}
        isNextDisabled={step === 3 || indicatorName === ""}
      />
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
        <VStack w="100%">
          <Heading size="lg" mb={4}>
            <Box display="inline" color="red.500">
              {dataPoints.length}
            </Box>{" "}
            data points for{" "}
            <Box display="inline" color="red.500">
              {indicatorName}
            </Box>
          </Heading>
          <HStack>
            <AddDataPointButton
              addDataPoint={addDataPoint}
              replaceDataPoint={replaceDataPoint}
            />
            <Button
              colorScheme="green"
              leftIcon={<AddIcon />}
              onClick={addBlankDataPoint}
            >
              New blank data point
            </Button>
          </HStack>
          <DataPointTable
            editDataPoint={editDataPoint}
            deleteDataPoint={deleteDataPoint}
            duplicateDataPoint={duplicateDataPoint}
            dataPoints={dataPoints}
            addDataPoint={addDataPoint}
            replaceDataPoint={replaceDataPoint}
          />
        </VStack>
      )}
      {step === 3 && <ReviewSubmit values={values} />}
    </VStack>
  );
};

export default IndicatorForm;
