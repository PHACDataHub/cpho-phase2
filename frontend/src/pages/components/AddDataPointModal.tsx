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
  HStack,
  VStack,
  Icon,
  Heading,
} from "@chakra-ui/react";
import { FormEvent, useState } from "react";
import { IndicatorDataFields } from "../../utils/constants";
import { useSmallScreen } from "../../utils/hooks";
import { DataPoint } from "../../utils/types";
import { IoIosGlobe } from "react-icons/io";
import { CgHashtag } from "react-icons/cg";
import { AiOutlineCalendar } from "react-icons/ai";

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

  const [fields, setFields] = useState<{
    yearType: "SINGLE" | "RANGE";
    year1: number;
    year2: number;
    geographyType: "COUNTRY" | "REGION" | "PROVINCE_TERRITORY";
    location: string;
  }>({
    yearType: dataPoint
      ? dataPoint.singleYearTimeframe
        ? "SINGLE"
        : "RANGE"
      : "SINGLE",
    year1: dataPoint
      ? (dataPoint.singleYearTimeframe as unknown as number) ?? 2022
      : 2022,
    year2: dataPoint
      ? (dataPoint.singleYearTimeframe as unknown as number) ?? 2022
      : 2022,
    geographyType: dataPoint
      ? (dataPoint.geography as "COUNTRY" | "REGION" | "PROVINCE_TERRITORY")
      : "COUNTRY",
    location: dataPoint ? dataPoint.country : "",
  });

  const { yearType, year1, year2, geographyType, location } = fields;

  // const handleSubmit = (event: FormEvent) => {
  // //   event.preventDefault();

  // //   console.log(event);
  // //   const point: DataPoint = {
  // //     country:
  // //       (document.getElementById("dp_location") as HTMLInputElement)?.value ??
  // //       "",
  // //     geography:
  // //       (document.getElementById("dp_geography") as HTMLInputElement)?.value ??
  // //       "",
  // //     sex: (document.getElementById("dp_sex") as HTMLInputElement)?.value ?? "",
  // //     gender:
  // //       (document.getElementById("dp_gender") as HTMLInputElement)?.value ?? "",
  // //     ageGroup:
  // //       (document.getElementById("dp_age_group") as HTMLInputElement).value ??
  // //       "",
  // //     ageGroupType:
  // //       (document.getElementById("dp_age_group_type") as HTMLInputElement)
  // //         .value ?? "",
  // //     dataQuality:
  // //       (document.getElementById("dp_data_quality") as HTMLInputElement)
  // //         .value ?? "",
  // //     value:
  // //       ((document.getElementById("dp_value") as HTMLInputElement)
  // //         .value as unknown as number) ?? 0,
  // //     valueUnit:
  // //       (document.getElementById("dp_value_unit") as HTMLInputElement).value ??
  // //       "",
  // //     valueLowerBound:
  // //       ((document.getElementById("dp_value_lower_bound") as HTMLInputElement)
  // //         .value as unknown as number) ?? 0,
  // //     valueUpperBound:
  // //       ((document.getElementById("dp_value_upper_bound") as HTMLInputElement)
  // //         .value as unknown as number) ?? 0,
  // //     singleYearTimeframe: yearType === "single" ? `${year1}` : undefined,
  // //     multiYearTimeframe:
  // //       yearType === "range" ? `${year1}-${year2}` : undefined,
  // //   };

  //   if (setDataPoints) {
  //     console.log(dataPoint);
  //     if (dataPoint) {
  //       console.log("Modifying existing data point at index ", dataPointIdx);
  //       setDataPoints(
  //         dataPoints
  //           .slice(0, dataPointIdx!)
  //           .concat([point])
  //           .concat(dataPoints.slice(dataPointIdx! + 1))
  //       );
  //     } else {
  //       setDataPoints([...dataPoints, point]);
  //     }
  //   }

  //   onClose();
  // };

  return (
    <Modal size="2xl" isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Add Data Point</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack w="100%" align="start" gap={5}>
            <VStack align="start">
              <HStack>
                <Icon as={IoIosGlobe} fontSize="xl" />
                <Heading size="md" display="flex" alignItems="center">
                  Geography
                </Heading>
              </HStack>
              <HStack>
                <FormControl isRequired>
                  <ButtonGroup isAttached>
                    <Button
                      size="sm"
                      isActive={geographyType === "COUNTRY"}
                      onClick={() =>
                        setFields({ ...fields, geographyType: "COUNTRY" })
                      }
                    >
                      Canada
                    </Button>
                    <Button
                      size="sm"
                      isActive={geographyType === "PROVINCE_TERRITORY"}
                      onClick={() =>
                        setFields({
                          ...fields,
                          geographyType: "PROVINCE_TERRITORY",
                        })
                      }
                    >
                      Province & Territory
                    </Button>
                    <Button
                      size="sm"
                      isActive={geographyType === "REGION"}
                      onClick={() =>
                        setFields({ ...fields, geographyType: "REGION" })
                      }
                    >
                      Region
                    </Button>
                  </ButtonGroup>
                </FormControl>
                {geographyType !== "COUNTRY" && (
                  <FormControl isRequired>
                    <Select
                      size="sm"
                      placeholder={`Select ${
                        geographyType === "PROVINCE_TERRITORY"
                          ? "Province/Territory"
                          : "Region"
                      }`}
                      value={
                        location ??
                        (geographyType === "REGION" ? "ATLANTIC" : "AB")
                      }
                      onChange={(event) =>
                        setFields({ ...fields, location: event.target.value })
                      }
                    >
                      {geographyType === "PROVINCE_TERRITORY" && (
                        <>
                          <option value="AB">Alberta</option>
                          <option value="BC">British Columbia</option>
                          <option value="MB">Manitoba</option>
                          <option value="NB">New Brunswick</option>
                          <option value="NL">Newfoundland and Labrador</option>
                          <option value="NS">Nova Scotia</option>
                          <option value="NT">Northwest Territories</option>
                          <option value="NU">Nunavut</option>
                          <option value="ON">Ontario</option>
                          <option value="PE">Prince Edward Island</option>
                          <option value="QC">Quebec</option>
                          <option value="SK">Saskatchewan</option>
                          <option value="YT">Yukon</option>
                        </>
                      )}
                      {geographyType === "REGION" && (
                        <>
                          <option value="ATLANTIC">Atlantic</option>
                          <option value="PRAIRIE">Prairie</option>
                          <option value="TERRITORIES">Territories</option>
                        </>
                      )}
                    </Select>
                  </FormControl>
                )}
              </HStack>
            </VStack>

            <VStack align="start">
              <HStack>
                <Icon as={CgHashtag} fontSize="xl" />
                <Heading size="md" display="flex" alignItems="center">
                  Value
                </Heading>
              </HStack>
              <NumberInput
                value={year2}
                onChange={(val) =>
                  setFields({
                    ...fields,
                    year2: val as unknown as number,
                  })
                }
                id="dp_date2"
                precision={0}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </VStack>

            <VStack align="start">
              <HStack>
                <Icon as={AiOutlineCalendar} fontSize="xl" />
                <Heading size="md" display="flex" alignItems="center">
                  Year
                </Heading>
              </HStack>

              <HStack w="100%" m={1} align="center">
                <FormControl isRequired>
                  <ButtonGroup isAttached>
                    <Button
                      size="sm"
                      onClick={() =>
                        setFields({ ...fields, yearType: "SINGLE" })
                      }
                      isActive={yearType === "SINGLE"}
                    >
                      Single Year
                    </Button>
                    <Button
                      size="sm"
                      onClick={() =>
                        setFields({ ...fields, yearType: "RANGE" })
                      }
                      isActive={yearType === "RANGE"}
                    >
                      Range
                    </Button>
                  </ButtonGroup>
                </FormControl>
                <FormControl isRequired>
                  <HStack>
                    <FormLabel htmlFor={"dp_date1"}>
                      {yearType === "RANGE" ? "From" : "Year"}
                    </FormLabel>
                    <NumberInput
                      min={1900}
                      max={3000}
                      value={year1}
                      onChange={(val) =>
                        setFields({
                          ...fields,
                          year1: val as unknown as number,
                        })
                      }
                      id="dp_date1"
                      precision={0}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </HStack>
                </FormControl>
                {yearType === "RANGE" && (
                  <FormControl isRequired>
                    <HStack>
                      <FormLabel htmlFor="dp_date2">{"To"}</FormLabel>{" "}
                      <NumberInput
                        min={1900}
                        max={3000}
                        value={year2}
                        onChange={(val) =>
                          setFields({
                            ...fields,
                            year2: val as unknown as number,
                          })
                        }
                        id="dp_date2"
                        precision={0}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </HStack>
                  </FormControl>
                )}
              </HStack>
            </VStack>
            {/* </Box> */}
          </VStack>
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
      </ModalContent>
    </Modal>
  );
}
