import { AddIcon } from "@chakra-ui/icons";
import { VStack, Button, Box, HStack, Heading } from "@chakra-ui/react";
import { useState } from "react";
import { DataPoint, IndicatorType, LocationType } from "../../utils/types";
import { AddDataPointButton } from "../molecules/AddDataPointButton";
import { DataPointTable } from "./DataPointTable";
import IndicatorGenInfo from "../molecules/IndicatorGenInfo";
import ReviewSubmit from "../molecules/ReviewSubmit";
import { v4 as uuidv4 } from "uuid";
import StepController from "../molecules/StepController";
import { categories, sub_categories } from "../../utils/constants";
import UpdateSubmit from "../molecules/UpdateSubmit";

const IndicatorForm = ({ indicator }: { indicator?: IndicatorType }) => {
  const [values, setValues] = useState({
    id: indicator?.id ?? 0,
    indicatorName: indicator?.name ?? "",
    detailedIndicator: indicator?.detailedIndicator ?? "",
    category: categories.find((c) => c.label === indicator?.category)?.id ?? 1,
    subCategory:
      sub_categories.find((c) => c.label === indicator?.subCategory)?.id ?? 1,
    dataPoints: (indicator?.indicatordataSet ?? []) as DataPoint[],
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
      id: uuidv4(),
      location: "CANADA",
      locationType: "COUNTRY",
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
      if (dataPoint.id === uuid) {
        if (field === "locationType") {
          const country: LocationType =
            value === "COUNTRY"
              ? "CANADA"
              : value === "REGION"
              ? "ATLANTIC"
              : "AB";

          return {
            ...dataPoint,
            locationType: value,
            location: country,
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
      if (dataPoint.id === uuid) {
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
      (dataPoint) => dataPoint.id !== uuid
    );
    setField("dataPoints", newDataPoints);
  };

  const duplicateDataPoint = (uuid: string) => {
    const idx = dataPoints.findIndex((dataPoint) => dataPoint.id === uuid);
    const dataPoint = dataPoints[idx];
    if (dataPoint) {
      setField(
        "dataPoints",
        dataPoints
          .slice(0, idx + 1)
          .concat({ ...dataPoint, id: uuidv4() }, dataPoints.slice(idx + 1))
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
      {step === 3 && !indicator && <ReviewSubmit values={values} />}
      {step === 3 && indicator && <UpdateSubmit values={values} />}
    </VStack>
  );
};

export default IndicatorForm;
