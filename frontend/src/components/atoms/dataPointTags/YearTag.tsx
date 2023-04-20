import {
  Box,
  Button,
  ButtonGroup,
  Editable,
  EditableInput,
  EditablePreview,
  HStack,
  Popover,
  PopoverArrow,
  PopoverContent,
  PopoverTrigger,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";

const YearTag = ({
  singleYear,
  multiYear,
  setSingleYear,
  setMultiYear,
  yearType,
  setYearType,
}: {
  singleYear?: number;
  multiYear?: [number, number];
  setSingleYear: (year?: number) => void;
  setMultiYear: (years?: [number, number]) => void;
  yearType: "SINGLE" | "RANGE";
  setYearType: (yearType: "SINGLE" | "RANGE") => void;
}) => {
  const [year1, setYear1] = useState(
    `${singleYear}` ??
      (multiYear ? `${multiYear[0]}` : `${new Date().getFullYear()}`)
  );
  const [year2, setYear2] = useState(
    `${singleYear}` ??
      (multiYear ? `${multiYear[1]}` : `${new Date().getFullYear()}`)
  );

  useEffect(() => {
    if (singleYear === undefined) {
      setYearType("RANGE");
      setYear1(multiYear ? `${multiYear[0]}` : `${new Date().getFullYear()}`);
      setYear2(multiYear ? `${multiYear[1]}` : `${new Date().getFullYear()}`);
    } else {
      setYearType("SINGLE");
      setYear1(`${singleYear}`);
    }
  }, [singleYear, multiYear, setYearType]);

  return (
    <Popover trigger="hover" placement="top">
      <PopoverTrigger>
        {yearType === "RANGE" ? (
          <HStack spacing={0.5}>
            <Box bgColor="gray.200" p={2} borderLeftRadius="md">
              <Editable
                value={year1}
                onChange={(val) => setYear1(val)}
                onSubmit={(val) => setMultiYear([Number(val), Number(year2)])}
              >
                <EditablePreview />
                <EditableInput />
              </Editable>
            </Box>
            <Box bgColor="gray.200" p={2} borderRightRadius="md">
              <Editable
                value={year2}
                onChange={(val) => setYear2(val)}
                onSubmit={(val) => setMultiYear([Number(year1), Number(val)])}
              >
                <EditablePreview />
                <EditableInput />
              </Editable>
            </Box>
          </HStack>
        ) : (
          <Box
            bgColor="gray.200"
            p={2}
            borderRadius="md"
            display="inline-block"
          >
            <Editable
              value={year1}
              onChange={(val) => setYear1(val)}
              onSubmit={(val) => setSingleYear(Number(val))}
            >
              <EditablePreview />
              <EditableInput />
            </Editable>
          </Box>
        )}
      </PopoverTrigger>
      <PopoverContent w="100%">
        <PopoverArrow />
        <ButtonGroup isAttached>
          <Button
            onClick={() => setYearType("SINGLE")}
            isActive={yearType === "SINGLE"}
            size="sm"
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
            Single
          </Button>
          <Button
            onClick={() => setYearType("RANGE")}
            isActive={yearType === "RANGE"}
            size="sm"
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
            Range
          </Button>
        </ButtonGroup>
      </PopoverContent>
    </Popover>
  );
};

export default YearTag;
