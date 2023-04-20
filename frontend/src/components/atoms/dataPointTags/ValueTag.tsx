import {
  Editable,
  EditableInput,
  EditablePreview,
  Input,
  VStack,
} from "@chakra-ui/react";
import { useContext, useEffect, useState } from "react";
import IndicatorFormContext from "../../../utils/context/IndicatorFormContext";

const ValueTag = ({
  unit,
  dataPointId,
}: {
  unit: string;
  dataPointId: string;
}) => {
  const { indicator, editDataPoint, addError, removeError, errors } =
    useContext(IndicatorFormContext);

  const dataPoint = indicator?.indicatordataSet.find(
    (dataPoint) => dataPoint.id === dataPointId
  );

  useEffect(() => {
    if (
      unit === "PERCENT" &&
      dataPoint &&
      (dataPoint.value < 0 || dataPoint.value > 100)
    ) {
      addError({
        dataPointId: dataPoint.id,
        field: "value",
        message: "Value must be between 0 and 100 for percentage indicators",
      });
    } else if (
      unit === "RATE" &&
      dataPoint &&
      (dataPoint.value < 0 || dataPoint.value > 100000)
    ) {
      addError({
        dataPointId: dataPoint.id,
        field: "value",
        message: "Value must be between 0 and 100k for rate indicators",
      });
    } else {
      removeError("value", dataPointId);
    }
  }, [unit, dataPoint, addError, removeError, dataPointId]);

  const setValue = (value: number) => {
    dataPoint && editDataPoint(dataPoint.id, "value", value);
  };

  const [tempValue, setTempValue] = useState(String(dataPoint?.value));

  useEffect(() => {
    setTempValue(dataPoint?.value ? String(dataPoint?.value) : "0");
  }, [dataPoint]);

  return (
    <VStack maxW={4}>
      <Editable
        display="inline-block"
        p={2}
        borderRadius="md"
        bgColor="gray.100"
        border={
          errors.find(
            (e) => e.field === "value" && e.dataPointId === dataPointId
          ) && "2px solid red"
        }
        value={tempValue}
        onChange={(val) => setTempValue(val)}
        onSubmit={(val) => setValue(Number(val))}
      >
        <EditablePreview />
        <Input as={EditableInput} variant="unstyled" minW="4em" maxW="6em" />
      </Editable>
    </VStack>
  );
};

export default ValueTag;
