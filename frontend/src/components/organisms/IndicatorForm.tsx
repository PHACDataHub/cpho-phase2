import { AddIcon } from "@chakra-ui/icons";
import { VStack, Button, Box, HStack, Heading } from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";
import { DataPoint, IndicatorType, LocationType } from "../../utils/types";
import { AddDataPointButton } from "../molecules/AddDataPointButton";
import { DataPointTable } from "./DataPointTable";
import IndicatorGenInfo from "../molecules/IndicatorGenInfo";
import ReviewSubmit from "../molecules/ReviewSubmit";
import { v4 as uuidv4 } from "uuid";
import StepController from "../molecules/StepController";
import { categories, sub_categories } from "../../utils/constants";
import UpdateSubmit from "../molecules/UpdateSubmit";
import { ErrorType } from "../../utils/types";
import { IndicatorFormProvider } from "../../utils/context/IndicatorFormContext";

const IndicatorForm = ({ indicator }: { indicator?: IndicatorType }) => {
  const [values, setValues] = useState({
    id: indicator?.id ?? 0,
    name: indicator?.name ?? "",
    detailedIndicator: indicator?.detailedIndicator ?? "",
    category: indicator?.category ?? "",
    subCategory: indicator?.subCategory ?? "",
    indicatordataSet: (indicator?.indicatordataSet ?? []) as DataPoint[],
    subIndicatorMeasurement: indicator?.subIndicatorMeasurement ?? "",
  } as IndicatorType);

  const [categoryId, setCategoryId] = useState(
    categories.find((c) => c.label === indicator?.category)?.id ?? 1
  );
  const [subCategoryId, setSubCategoryId] = useState(
    sub_categories.find((c) => c.label === indicator?.subCategory)?.id ?? 1
  );

  const [errors, setErrors] = useState<ErrorType[]>([]);

  const {
    name: indicatorName,
    category,
    subCategory,
    indicatordataSet: dataPoints,
  } = values;

  useEffect(() => {
    setCategoryId(categories.find((c) => c.label === category)?.id ?? 1);
  }, [category]);

  useEffect(() => {
    setSubCategoryId(
      sub_categories.find((c) => c.label === subCategory)?.id ?? 1
    );
  }, [subCategory]);

  const setField = useCallback(
    (field: string, value: any) => {
      setValues({
        ...values,
        [field]: value,
      } as IndicatorType);
    },
    [values]
  );

  const [step, setStep] = useState(1);

  const addBlankDataPoint = useCallback(() => {
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
    setField("indicatordataSet", [dataPoint, ...dataPoints]);
  }, [dataPoints, setField]);

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
        return dataPoint;
      };
      setField("indicatordataSet", newDataPoints);
    },
    [dataPoints, setField]
  );

  const replaceDataPoint = useCallback(
    (uuid: string, newDataPoint: DataPoint) => {
      const newDataPoints = dataPoints.map((dataPoint) => {
        if (dataPoint.id === uuid) {
          return newDataPoint;
        }
        return dataPoint;
      });
      setField("indicatordataSet", newDataPoints);
    },
    [dataPoints, setField]
  );

  const addDataPoint = useCallback(
    (newDataPoint: DataPoint) => {
      setField("indicatordataSet", [newDataPoint, ...dataPoints]);
    },
    [dataPoints, setField]
  );

  const deleteDataPoint = useCallback(
    (uuid: string) => {
      const newDataPoints = dataPoints.filter(
        (dataPoint) => dataPoint.id !== uuid
      );
      setField("indicatordataSet", newDataPoints);
    },
    [dataPoints, setField]
  );

  const duplicateDataPoint = useCallback(
    (uuid: string) => {
      const idx = dataPoints.findIndex((dataPoint) => dataPoint.id === uuid);

      const dataPoint = dataPoints[idx];

      if (dataPoint) {
        setField(
          "indicatordataSet",
          dataPoints
            .slice(0, idx + 1)
            .concat({ ...dataPoint, id: uuidv4() }, dataPoints.slice(idx + 1))
        );
      }
    },
    [dataPoints, setField]
  );

  const addError = useCallback(
    (error: ErrorType) => {
      const temp = errors.find(
        (e) => e.field === error.field && e.dataPointId === error.dataPointId
      );
      if (temp) {
        if (temp.message === error.message) return;
        setErrors((errors) =>
          errors.map((e) => {
            if (
              e.field === error.field &&
              e.dataPointId === error.dataPointId
            ) {
              return {
                ...e,
                message: error.message,
              };
            }
            return e;
          })
        );
      } else {
        setErrors((errors) => [...errors, error]);
      }
    },
    [errors]
  );

  const removeError = useCallback(
    (field: string, dataPointId: string) => {
      if (
        !errors.find((e) => e.field === field && e.dataPointId === dataPointId)
      )
        return;
      setErrors((errors) =>
        errors.filter(
          (error) => error.field !== field || error.dataPointId !== dataPointId
        )
      );
    },
    [errors]
  );

  const clearRowErrors = useCallback(
    (dataPointId: string) => {
      if (!errors.find((e) => e.dataPointId === dataPointId)) return;
      setErrors((errors) =>
        errors.filter((error) => error.dataPointId !== dataPointId)
      );
    },
    [setErrors, errors]
  );

  return (
    <IndicatorFormProvider
      value={{
        indicator: values,
        setField,
        addBlankDataPoint,
        editDataPoint,
        replaceDataPoint,
        addDataPoint,
        deleteDataPoint,
        duplicateDataPoint,
        errors,
        addError,
        removeError,
        clearRowErrors,
        step,
        setStep,
      }}
    >
      <VStack w="100%">
        <StepController
          isPrevDisabled={step === 1}
          isNextDisabled={step === 3 || indicatorName === ""}
        />
        {step === 1 && (
          <IndicatorGenInfo
            categoryId={categoryId}
            subCategoryId={subCategoryId}
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
              <AddDataPointButton />
              <Button
                colorScheme="green"
                leftIcon={<AddIcon />}
                onClick={addBlankDataPoint}
              >
                New blank data point
              </Button>
            </HStack>
            <DataPointTable />
          </VStack>
        )}
        {step === 3 && !indicator && <ReviewSubmit values={values} />}
        {step === 3 && indicator && <UpdateSubmit values={values} />}
      </VStack>
    </IndicatorFormProvider>
  );
};

export default IndicatorForm;
