import {
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
  ButtonGroup,
  Button,
  ModalFooter,
  Select,
  HStack,
  VStack,
  Icon,
  Heading,
  IconButton,
  Divider,
} from "@chakra-ui/react";
import { useState } from "react";
import { DataPoint } from "../../utils/types";
import { IoIosGlobe, IoMdClose } from "react-icons/io";
import { CgHashtag } from "react-icons/cg";
import { AiOutlineCalendar, AiOutlineWarning } from "react-icons/ai";
import { BsStar, BsStarFill } from "react-icons/bs";
import { FaRegThumbsUp } from "react-icons/fa";

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
  const dataPoint = dataPoints[dataPointIdx!];

  const [fields, setFields] = useState<{
    yearType: "SINGLE" | "RANGE";
    year1: number;
    year2: number;
    geographyType: "COUNTRY" | "REGION" | "PROVINCE_TERRITORY";
    location: string;
    value: string;
    valueUnit: string;
    valueUnitOther: string;
    valueUpperBound?: string;
    valueLowerBound?: string;
    dataQuality: "CAUTION" | "ACCEPTABLE" | "GOOD" | "EXCELLENT";
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
    value: dataPoint ? String(dataPoint.value) : "0",
    valueUnit: dataPoint ? dataPoint.valueUnit : "",
    valueUnitOther: "",
    valueUpperBound: dataPoint ? String(dataPoint.valueUpperBound) : "0",
    valueLowerBound: dataPoint ? String(dataPoint.valueLowerBound) : "0",
    dataQuality: dataPoint
      ? (dataPoint.dataQuality as
          | "CAUTION"
          | "ACCEPTABLE"
          | "GOOD"
          | "EXCELLENT")
      : "ACCEPTABLE",
  });

  const {
    yearType,
    year1,
    year2,
    geographyType,
    location,
    value,
    valueLowerBound,
    valueUpperBound,
    dataQuality,
    valueUnit,
    valueUnitOther,
  } = fields;

  const [showUpperBound, setShowUpperBound] = useState(false);
  const [showLowerBound, setShowLowerBound] = useState(false);
  const [showAgeInfo, setShowAgeInfo] = useState(false);
  const [showSexInfo, setShowSexInfo] = useState(false);
  const [showGenderInfo, setShowGenderInfo] = useState(false);

  return (
    <Modal size="2xl" isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Add Data Point</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack w="100%" align="start" gap={3}>
            {/* GEOGRAPHY */}
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
            <Divider />

            {/* VALUE */}

            <VStack align="start">
              <HStack>
                <Icon as={CgHashtag} fontSize="xl" />
                <Heading size="md" display="flex" alignItems="center">
                  Value
                </Heading>
                <NumberInput
                  maxW="150px"
                  precision={2}
                  step={0.01}
                  value={value}
                  onChange={(val) =>
                    setFields({
                      ...fields,
                      value: val,
                    })
                  }
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <Heading size="md">Unit:</Heading>
                <ButtonGroup isAttached>
                  <Button
                    size="sm"
                    isActive={valueUnit === "PERCENT"}
                    onClick={() =>
                      setFields({ ...fields, valueUnit: "PERCENT" })
                    }
                  >
                    %
                  </Button>
                  <Button
                    size="sm"
                    isActive={valueUnit === "RATE"}
                    onClick={() => setFields({ ...fields, valueUnit: "RATE" })}
                  >
                    Per 100k
                  </Button>
                  <Button
                    size="sm"
                    isActive={valueUnit === "OTHER"}
                    onClick={() => setFields({ ...fields, valueUnit: "OTHER" })}
                  >
                    Other
                  </Button>
                </ButtonGroup>
              </HStack>
              <HStack align="end" gap={3}>
                {valueUnit === "OTHER" && (
                  <Input
                    maxW="150px"
                    size="sm"
                    value={valueUnitOther}
                    onChange={(event) =>
                      setFields({
                        ...fields,
                        valueUnitOther: event.target.value,
                      })
                    }
                    placeholder="Enter unit"
                  />
                )}
                {!showUpperBound && (
                  <Button
                    px={5}
                    onClick={() => setShowUpperBound(true)}
                    size="sm"
                  >
                    Add Upper Bound
                  </Button>
                )}
                {showUpperBound && (
                  <VStack align="start">
                    <HStack w="100%" justify="space-between">
                      <Heading size="sm">Upper Bound</Heading>
                      <IconButton
                        size="sm"
                        aria-label="Remove Upper Bound"
                        icon={<Icon as={IoMdClose} />}
                        onClick={() => setShowUpperBound(false)}
                      />
                    </HStack>
                    <NumberInput
                      precision={2}
                      step={0.01}
                      value={valueUpperBound}
                      onChange={(val) =>
                        setFields({
                          ...fields,
                          valueUpperBound: val,
                        })
                      }
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </VStack>
                )}
                {!showLowerBound && (
                  <Button
                    px={5}
                    onClick={() => setShowLowerBound(true)}
                    size="sm"
                  >
                    Add Lower Bound
                  </Button>
                )}
                {showLowerBound && (
                  <VStack align="start">
                    <HStack w="100%" justify="space-between">
                      <Heading size="sm">Lower Bound</Heading>

                      <IconButton
                        size="sm"
                        aria-label="Remove Lower Bound"
                        icon={<Icon as={IoMdClose} />}
                        onClick={() => setShowLowerBound(false)}
                      />
                    </HStack>
                    <NumberInput
                      precision={2}
                      step={0.01}
                      value={valueLowerBound}
                      onChange={(val) =>
                        setFields({
                          ...fields,
                          valueLowerBound: val,
                        })
                      }
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </VStack>
                )}
              </HStack>
            </VStack>

            <Divider />

            {/* YEAR */}

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

            <Divider />

            {/* DATA QUALITY */}

            <VStack align="start">
              <Heading size="md" display="flex" alignItems="center">
                Data Quality
              </Heading>
              <ButtonGroup isAttached>
                <Button
                  size="sm"
                  leftIcon={<Icon as={AiOutlineWarning} />}
                  isActive={dataQuality === "CAUTION"}
                  onClick={() =>
                    setFields({ ...fields, dataQuality: "CAUTION" })
                  }
                >
                  Caution
                </Button>
                <Button
                  size="sm"
                  leftIcon={<Icon as={FaRegThumbsUp} />}
                  isActive={dataQuality === "ACCEPTABLE"}
                  onClick={() =>
                    setFields({ ...fields, dataQuality: "ACCEPTABLE" })
                  }
                >
                  Acceptable
                </Button>
                <Button
                  size="sm"
                  leftIcon={<Icon as={BsStar} />}
                  isActive={dataQuality === "GOOD"}
                  onClick={() => setFields({ ...fields, dataQuality: "GOOD" })}
                >
                  Good
                </Button>
                <Button
                  size="sm"
                  leftIcon={<Icon as={BsStarFill} />}
                  isActive={dataQuality === "EXCELLENT"}
                  onClick={() =>
                    setFields({ ...fields, dataQuality: "EXCELLENT" })
                  }
                >
                  Excellent
                </Button>
              </ButtonGroup>
            </VStack>

            <Divider />

            {showAgeInfo && (
              <>
                <VStack align="start" w="100%">
                  <HStack w="100%" justify="space-between">
                    <Heading size="md" display="flex" alignItems="center">
                      Age
                    </Heading>
                    <IconButton
                      size="sm"
                      aria-label="Remove Age"
                      icon={<Icon as={IoMdClose} />}
                      onClick={() => setShowAgeInfo(false)}
                    />
                  </HStack>
                </VStack>
                <Divider />
              </>
            )}

            {showSexInfo && (
              <>
                <VStack align="start" w="100%">
                  <HStack w="100%" justify="space-between">
                    <Heading size="md" display="flex" alignItems="center">
                      Sex
                    </Heading>
                    <IconButton
                      size="sm"
                      aria-label="Remove Sex"
                      icon={<Icon as={IoMdClose} />}
                      onClick={() => setShowSexInfo(false)}
                    />
                  </HStack>
                </VStack>

                <Divider />
              </>
            )}

            {showGenderInfo && (
              <>
                <VStack align="start" w="100%">
                  <HStack w="100%" justify="space-between">
                    <Heading size="md" display="flex" alignItems="center">
                      Gender
                    </Heading>
                    <IconButton
                      size="sm"
                      aria-label="Remove Gender"
                      icon={<Icon as={IoMdClose} />}
                      onClick={() => setShowGenderInfo(false)}
                    />
                  </HStack>
                </VStack>

                <Divider />
              </>
            )}

            <ButtonGroup>
              {!showAgeInfo && (
                <Button size="sm" onClick={() => setShowAgeInfo(true)}>
                  Add Age
                </Button>
              )}
              {!showSexInfo && (
                <Button size="sm" onClick={() => setShowSexInfo(true)}>
                  Add Sex
                </Button>
              )}
              {!showGenderInfo && (
                <Button size="sm" onClick={() => setShowGenderInfo(true)}>
                  Add Gender
                </Button>
              )}
            </ButtonGroup>
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
