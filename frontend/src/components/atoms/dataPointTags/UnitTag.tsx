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
import { useEffect, useState } from "react";

const UnitTag = ({
  unit,
  setUnit,
}: {
  unit: string;
  setUnit: (unit: string) => void;
}) => {
  const [label, color] = (() => {
    switch (unit) {
      case "PERCENT":
        return ["%", "green.100"];
      case "RATE":
        return ["Per 100k", "blue.100"];
      default:
        return [unit, "gray.100"];
    }
  })();

  const [unitOther, setUnitOther] = useState("");

  useEffect(() => {
    setUnitOther(unit);
  }, [unit]);

  return (
    <Popover placement="right" trigger="hover">
      <PopoverTrigger>
        <Box
          bgColor={color}
          p={2}
          borderRadius="md"
          display="inline-block"
          cursor="pointer"
          transition="all 0.2s ease-in-out"
          _hover={{ transform: "scale(1.075)" }}
        >
          {unit === "OTHER" ? (
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
        <PopoverArrow />
        <VStack spacing={0} align="stretch">
          <Button
            borderRadius={0}
            borderTopRadius="md"
            isActive={unit === "PERCENT"}
            size="sm"
            onClick={() => setUnit("PERCENT")}
            _dark={{
              color: "white",
              bgColor: "gray.800",
              _hover: {
                bgColor: "gray.700",
              },
              _active: {
                bgColor: "gray.600",
              },
            }}
          >
            %
          </Button>
          <Button
            borderRadius={0}
            isActive={unit === "RATE"}
            size="sm"
            onClick={() => setUnit("RATE")}
            _dark={{
              color: "white",
              bgColor: "gray.800",
              _hover: {
                bgColor: "gray.700",
              },
              _active: {
                bgColor: "gray.600",
              },
            }}
          >
            Per 100k
          </Button>
          <Button
            borderRadius={0}
            borderBottomRadius="md"
            isActive={unit === "OTHER"}
            size="sm"
            onClick={() => setUnit("OTHER")}
            _dark={{
              color: "white",
              bgColor: "gray.800",
              _hover: {
                bgColor: "gray.700",
              },
              _active: {
                bgColor: "gray.600",
              },
            }}
          >
            Other
          </Button>
        </VStack>
      </PopoverContent>
    </Popover>
  );
};

export default UnitTag;
