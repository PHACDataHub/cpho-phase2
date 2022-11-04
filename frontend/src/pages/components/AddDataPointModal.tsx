import {
  Box,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  FormControl,
  FormLabel,
  Input,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Stack,
  ButtonGroup,
  Button,
  ModalFooter,
  Select,
} from "@chakra-ui/react";
import { FormEvent, useState } from "react";
import { IndicatorDataFields } from "../../utils/constants";
import { useSmallScreen } from "../../utils/hooks";
import { DataPoint } from "../../utils/types";

export function AddDataPointModal({
  dataPointIdx,
  dataPoints,
  setDataPoints,
  isOpen,
  onClose,
}: {
  dataPointIdx?: number;
  dataPoints: DataPoint[];
  setDataPoints?: (dataPoints: DataPoint[]) => void;
  isOpen: boolean;
  onClose: () => void;
}): JSX.Element {
  const smallScreen = useSmallScreen();

  const dataPoint = dataPoints[dataPointIdx!];

  const [yearType, setYearType] = useState<"single" | "range">(
    dataPoint ? (dataPoint.singleYearTimeframe ? "single" : "range") : "single"
  );
  const [year1, setYear1] = useState<number>(
    dataPoint
      ? (dataPoint.singleYearTimeframe as unknown as number) ?? 2022
      : 2022
  );
  const [year2, setYear2] = useState<number>(2023);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();

    console.log(event);
    const point: DataPoint = {
      country:
        (document.getElementById("dp_location") as HTMLInputElement)?.value ??
        "",
      geography:
        (document.getElementById("dp_geography") as HTMLInputElement)?.value ??
        "",
      sex: (document.getElementById("dp_sex") as HTMLInputElement)?.value ?? "",
      gender:
        (document.getElementById("dp_gender") as HTMLInputElement)?.value ?? "",
      ageGroup:
        (document.getElementById("dp_age_group") as HTMLInputElement).value ??
        "",
      ageGroupType:
        (document.getElementById("dp_age_group_type") as HTMLInputElement)
          .value ?? "",
      dataQuality:
        (document.getElementById("dp_data_quality") as HTMLInputElement)
          .value ?? "",
      value:
        ((document.getElementById("dp_value") as HTMLInputElement)
          .value as unknown as number) ?? 0,
      valueUnit:
        (document.getElementById("dp_value_unit") as HTMLInputElement).value ??
        "",
      valueLowerBound:
        ((document.getElementById("dp_value_lower_bound") as HTMLInputElement)
          .value as unknown as number) ?? 0,
      valueUpperBound:
        ((document.getElementById("dp_value_upper_bound") as HTMLInputElement)
          .value as unknown as number) ?? 0,
      singleYearTimeframe: yearType === "single" ? `${year1}` : undefined,
      multiYearTimeframe:
        yearType === "range" ? `${year1}-${year2}` : undefined,
    };

    if (setDataPoints) {
      console.log(dataPoint);
      if (dataPoint) {
        console.log("Modifying existing data point at index ", dataPointIdx);
        setDataPoints(
          dataPoints
            .slice(0, dataPointIdx!)
            .concat([point])
            .concat(dataPoints.slice(dataPointIdx! + 1))
        );
      } else {
        setDataPoints([...dataPoints, point]);
      }
    }

    onClose();
  };

  return (
    <Modal size="2xl" isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Add Data Point</ModalHeader>
        <ModalCloseButton />

        <form onSubmit={handleSubmit}>
          <ModalBody>
            <Box display="flex" flexWrap="wrap" alignContent="stretch">
              {IndicatorDataFields.map((field) => {
                // console.log("field: ", field);
                // console.log(
                //   "dataPoint: ",
                //   dataPoint && dataPoint[field.dpField]
                // );
                return (
                  <Box
                    key={field.id}
                    flexGrow={1}
                    w={smallScreen ? "100%" : "45%"}
                    m={3}
                  >
                    <FormControl isRequired={field.required}>
                      <FormLabel htmlFor={field.id}>{field.name}</FormLabel>
                      {field.type === "text" ? (
                        <Input
                          placeholder={field.placeholder ?? ""}
                          id={field.id}
                          defaultValue={dataPoint && dataPoint[field.dpField]}
                        />
                      ) : field.type === "number" ? (
                        <NumberInput
                          defaultValue={dataPoint && dataPoint[field.dpField]}
                          id={field.id}
                          precision={2}
                          step={0.01}
                        >
                          <NumberInputField />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>
                      ) : (
                        field.options && (
                          <Select
                            id={field.id}
                            placeholder={`Select ${field.name}`}
                            defaultValue={dataPoint && dataPoint[field.dpField]}
                          >
                            {field.options.map((option, idx) => (
                              <option key={idx} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </Select>
                        )
                      )}
                    </FormControl>
                  </Box>
                );
              })}
              <Stack w="100%" m={3}>
                <FormControl isRequired>
                  <ButtonGroup isAttached>
                    <Button
                      size="sm"
                      onClick={() => setYearType("single")}
                      isActive={yearType === "single"}
                    >
                      Single Year
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => setYearType("range")}
                      isActive={yearType === "range"}
                    >
                      Range
                    </Button>
                  </ButtonGroup>
                </FormControl>
                <FormControl isRequired>
                  <FormLabel htmlFor={"dp_date1"}>
                    {yearType === "range" ? "From" : "Year"}
                  </FormLabel>
                  <NumberInput
                    min={1900}
                    max={3000}
                    value={year1}
                    onChange={(val) => setYear1(val as unknown as number)}
                    id="dp_date1"
                    precision={0}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                {yearType === "range" && (
                  <FormControl>
                    <FormLabel htmlFor="dp_date2">{"To"}</FormLabel>{" "}
                    <NumberInput
                      min={1900}
                      max={3000}
                      value={year2}
                      onChange={(val) => setYear2(val as unknown as number)}
                      id="dp_date2"
                      precision={0}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </FormControl>
                )}
              </Stack>
            </Box>
          </ModalBody>
          <ModalFooter>
            <Button
              type="submit"
              colorScheme="green"
              mr={3}
              float="right"
              // onClick={handleSubmit}
            >
              Save
            </Button>
            <Button colorScheme="red" onClick={onClose}>
              Cancel
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
}
