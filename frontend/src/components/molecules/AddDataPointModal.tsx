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
import { FormEvent, useEffect, useState } from "react";
import { DataPoint, LocationType } from "../../utils/types";
import { IoIosGlobe, IoMdClose } from "react-icons/io";
import { CgHashtag } from "react-icons/cg";
import { AiOutlineCalendar, AiOutlineWarning } from "react-icons/ai";
import { BsStar, BsStarFill } from "react-icons/bs";
import { FaRegThumbsUp } from "react-icons/fa";
import { v4 as uuidv4 } from "uuid";

export function AddDataPointModal({
  dataPoint,
  yearType,
  setYearType,
  replaceDataPoint,
  addDataPoint,
  isOpen,
  onClose,
}: {
  dataPoint?: DataPoint;
  yearType: "SINGLE" | "RANGE";
  setYearType: (yearType: "SINGLE" | "RANGE") => void;
  replaceDataPoint: (uuid: string, dataPoint: DataPoint) => void;
  addDataPoint: (dataPoint: DataPoint) => void;
  isOpen: boolean;
  onClose: () => void;
}): JSX.Element {
  const [dp, setDp] = useState<DataPoint>(
    dataPoint ?? {
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
    }
  );

  const [valueUnitOther, setValueUnitOther] = useState<string>("");

  const {
    id,
    locationType,
    location,
    value,
    singleYearTimeframe,
    multiYearTimeframe,
    valueLowerBound,
    valueUpperBound,
    dataQuality,
    valueUnit,
  } = dp ?? {};

  const [fromYear, setFromYear] = useState<number>(
    singleYearTimeframe ?? (multiYearTimeframe && multiYearTimeframe[0]) ?? 2022
  );
  const [toYear, setToYear] = useState<number>(
    singleYearTimeframe ?? (multiYearTimeframe && multiYearTimeframe[1]) ?? 2022
  );

  useEffect(() => {
    if (yearType === "SINGLE") {
      setFromYear(singleYearTimeframe ?? 2022);
      setToYear(singleYearTimeframe ?? 2022);
    } else {
      setFromYear((multiYearTimeframe && multiYearTimeframe[0]) ?? 2022);
      setToYear((multiYearTimeframe && multiYearTimeframe[1]) ?? 2022);
    }
  }, [singleYearTimeframe, multiYearTimeframe, yearType]);

  const [tempValue, setTempValue] = useState(String(value));

  useEffect(() => {
    setTempValue(String(value));
  }, [value]);

  const [showUpperBound, setShowUpperBound] = useState(false);
  const [showLowerBound, setShowLowerBound] = useState(false);
  const [showAgeInfo, setShowAgeInfo] = useState(false);
  const [showSexInfo, setShowSexInfo] = useState(false);
  const [showGenderInfo, setShowGenderInfo] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const point: DataPoint = {
      id,
      locationType,
      location,
      sex: "",
      gender: "",
      ageGroup: "",
      ageGroupType: "",
      dataQuality,
      value: Number(tempValue),
      valueLowerBound: Number(valueLowerBound),
      valueUpperBound: Number(valueUpperBound),
      valueUnit: valueUnitOther ? valueUnitOther : valueUnit,
      singleYearTimeframe: yearType === "SINGLE" ? fromYear : undefined,
      multiYearTimeframe: yearType === "RANGE" ? [fromYear, toYear] : undefined,
    };

    if (dataPoint) {
      replaceDataPoint(id, point);
    } else {
      addDataPoint(point);
    }
    onClose();
  };

  useEffect(() => {
    if (dataPoint) {
      setDp({
        ...dataPoint,
      });
    }
  }, [dataPoint]);

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
                      isActive={locationType === "COUNTRY"}
                      onClick={() => {
                        setDp({
                          ...dp,
                          locationType: "COUNTRY",
                          location: "CANADA",
                        });
                      }}
                    >
                      Canada
                    </Button>
                    <Button
                      size="sm"
                      isActive={locationType === "PROVINCE_TERRITORY"}
                      onClick={() =>
                        setDp({
                          ...dp,
                          locationType: "PROVINCE_TERRITORY",
                          location: "AB",
                        })
                      }
                    >
                      Province & Territory
                    </Button>
                    <Button
                      size="sm"
                      isActive={locationType === "REGION"}
                      onClick={() =>
                        setDp({
                          ...dp,
                          locationType: "REGION",
                          location: "ATLANTIC",
                        })
                      }
                    >
                      Region
                    </Button>
                  </ButtonGroup>
                </FormControl>
                {locationType !== "COUNTRY" && (
                  <FormControl isRequired>
                    <Select
                      size="sm"
                      placeholder={`Select ${
                        locationType === "PROVINCE_TERRITORY"
                          ? "Province/Territory"
                          : "Region"
                      }`}
                      value={locationType}
                      onChange={(event) =>
                        setDp({
                          ...dp,
                          location: event.target.value as LocationType,
                        })
                      }
                    >
                      {locationType === "PROVINCE_TERRITORY" && (
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
                      {locationType === "REGION" && (
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
                  value={tempValue}
                  onChange={(valueString) => setTempValue(valueString)}
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
                      setDp({
                        ...dp,
                        valueUnit: "PERCENT",
                      })
                    }
                  >
                    %
                  </Button>
                  <Button
                    size="sm"
                    isActive={valueUnit === "RATE"}
                    onClick={() => setDp({ ...dp, valueUnit: "RATE" })}
                  >
                    Per 100k
                  </Button>
                  <Button
                    size="sm"
                    isActive={valueUnit === "OTHER"}
                    onClick={() => setDp({ ...dp, valueUnit: "OTHER" })}
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
                    onChange={(event) => setValueUnitOther(event.target.value)}
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
                        setDp({
                          ...dp,
                          valueUpperBound: Number(val),
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
                        setDp({
                          ...dp,
                          valueLowerBound: Number(val),
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
                      onClick={() => setYearType("SINGLE")}
                      isActive={yearType === "SINGLE"}
                    >
                      Single Year
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => setYearType("RANGE")}
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
                      value={fromYear}
                      onChange={(val) => setFromYear(Number(val))}
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
                        value={toYear}
                        onChange={(val) =>
                          setToYear(
                            Number(val) > fromYear ? Number(val) : fromYear
                          )
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
                    setDp({
                      ...dp,
                      dataQuality: "CAUTION",
                    })
                  }
                >
                  Caution
                </Button>
                <Button
                  size="sm"
                  leftIcon={<Icon as={FaRegThumbsUp} />}
                  isActive={dataQuality === "ACCEPTABLE"}
                  onClick={() =>
                    setDp({
                      ...dp,
                      dataQuality: "ACCEPTABLE",
                    })
                  }
                >
                  Acceptable
                </Button>
                <Button
                  size="sm"
                  leftIcon={<Icon as={BsStar} />}
                  isActive={dataQuality === "GOOD"}
                  onClick={() => setDp({ ...dp, dataQuality: "GOOD" })}
                >
                  Good
                </Button>
                <Button
                  size="sm"
                  leftIcon={<Icon as={BsStarFill} />}
                  isActive={dataQuality === "EXCELLENT"}
                  onClick={() =>
                    setDp({
                      ...dp,
                      dataQuality: "EXCELLENT",
                    })
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
            onClick={handleSubmit}
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
