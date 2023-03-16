import {
  Box,
  Button,
  Editable,
  EditableInput,
  EditablePreview,
  Heading,
  Popover,
  PopoverArrow,
  PopoverContent,
  PopoverTrigger,
  VStack,
} from "@chakra-ui/react";
import { useContext, useEffect, useState } from "react";
import IndicatorFormContext from "../../../utils/context/IndicatorFormContext";

const UnitTag = ({
  setUnit,
  dataPointId,
}: {
  setUnit: (unit: string) => void;
  dataPointId: string;
}) => {
  const { errors, indicator } = useContext(IndicatorFormContext);
  const dataPoint = indicator?.indicatordataSet.find(
    (dataPoint) => dataPoint.id === dataPointId
  );

  const [label, color] = (() => {
    switch (dataPoint?.valueUnit) {
      case "PERCENT":
        return ["%", "green.100"];
      case "RATE":
        return ["Per 100k", "blue.100"];
      default:
        return [dataPoint?.valueUnit, "gray.100"];
    }
  })();

  const [unitOther, setUnitOther] = useState("");

  useEffect(() => {
    setUnitOther(dataPoint?.valueUnit ?? "");
  }, [dataPoint?.valueUnit]);

  const err = errors.find(
    (err) => err.field === "value" && err.dataPointId === dataPointId
  );

  return (
    <Popover placement="right" trigger="hover">
      <PopoverTrigger>
        <Box
          bgColor={color}
          border={err && "2px solid red"}
          p={2}
          borderRadius="md"
          display="inline-block"
          cursor="pointer"
          transition="all 0.2s ease-in-out"
          _hover={{ transform: "scale(1.075)" }}
        >
          {dataPoint?.valueUnit === "OTHER" ? (
            <Editable
              value={unitOther}
              onChange={(val) => setUnitOther(val)}
              onSubmit={(val) => setUnit(val)}
            >
              <EditablePreview />
              <EditableInput minW="6em" maxW="8em" />
            </Editable>
          ) : (
            <Heading size="xs">{label}</Heading>
          )}
        </Box>
      </PopoverTrigger>
      <PopoverContent w="100%">
        <PopoverArrow bgColor="gray.100" />
        <VStack spacing={0} align="stretch">
          <Button
            borderRadius={0}
            borderTopRadius="md"
            isActive={dataPoint?.valueUnit === "PERCENT"}
            size="sm"
            onClick={() => setUnit("PERCENT")}
          >
            %
          </Button>
          <Button
            borderRadius={0}
            isActive={dataPoint?.valueUnit === "RATE"}
            size="sm"
            onClick={() => setUnit("RATE")}
          >
            Per 100k
          </Button>
          <Button
            borderRadius={0}
            borderBottomRadius="md"
            isActive={dataPoint?.valueUnit === "OTHER"}
            size="sm"
            onClick={() => setUnit("OTHER")}
          >
            Other
          </Button>
        </VStack>
      </PopoverContent>
    </Popover>
  );
};

export default UnitTag;
