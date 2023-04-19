import { CopyIcon, DeleteIcon, EditIcon, WarningIcon } from "@chakra-ui/icons";
import {
  Tr,
  Td,
  HStack,
  IconButton,
  ButtonGroup,
  useDisclosure,
  Text,
} from "@chakra-ui/react";
import { DataPoint, LocationType } from "../../utils/types";
import { AddDataPointModal } from "../molecules/AddDataPointModal";
import LocationTypeTag from "../atoms/dataPointTags/LocationTypeTag";
import LocationTag from "../atoms/dataPointTags/LocationTag";
import DataQualityTag from "../atoms/dataPointTags/DataQualityTag";
import YearTag from "../atoms/dataPointTags/YearTag";
import UnitTag from "../atoms/dataPointTags/UnitTag";
import ValueTag from "../atoms/dataPointTags/ValueTag";
import { useContext, useMemo, useState } from "react";
import IndicatorFormContext from "../../utils/context/IndicatorFormContext";

const DataPointRow = ({ dataPoint }: { dataPoint: DataPoint }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const {
    indicator,
    deleteDataPoint,
    duplicateDataPoint,
    replaceDataPoint,
    addDataPoint,
    editDataPoint,
    errors,
  } = useContext(IndicatorFormContext);
  const idx = indicator?.indicatordataSet.indexOf(dataPoint);
  const rowErrors = useMemo(
    () => errors.filter((e) => e.dataPointId === dataPoint.id),
    [errors, dataPoint.id]
  );

  const [yearType, setYearType] = useState<"SINGLE" | "RANGE">(
    dataPoint.multiYearTimeframe === undefined ? "SINGLE" : "RANGE"
  );

  const onDelete = () => deleteDataPoint(dataPoint.id);
  const onDuplicate = () => duplicateDataPoint(dataPoint.id);

  return (
    <>
      <Tr
        key={dataPoint.id}
        _hover={{
          bgColor: rowErrors.length > 0 ? "red.100" : "gray.50",
        }}
        bgColor={rowErrors.length > 0 ? "red.100" : "white"}
      >
        <Td isNumeric>{(idx ?? -1) + 1}</Td>
        <Td>
          <HStack spacing={2}>
            <ButtonGroup isAttached>
              <IconButton
                size="sm"
                aria-label="Delete Data Point"
                colorScheme="red"
                icon={<DeleteIcon />}
                onClick={onDelete}
              />
              <IconButton
                size="sm"
                aria-label="Duplicate Data Point"
                colorScheme="blue"
                icon={<CopyIcon />}
                onClick={onDuplicate}
              />
              <IconButton
                size="sm"
                aria-label="Edit Data Point"
                colorScheme="green"
                icon={<EditIcon />}
                onClick={onOpen}
              />
            </ButtonGroup>
          </HStack>
          <AddDataPointModal
            dataPoint={dataPoint}
            isOpen={isOpen}
            onClose={onClose}
            replaceDataPoint={replaceDataPoint}
            addDataPoint={addDataPoint}
            yearType={yearType}
            setYearType={setYearType}
          />
        </Td>
        <Td>
          <LocationTypeTag
            type={dataPoint.locationType}
            setGeography={(geography: string) => {
              editDataPoint(dataPoint.id, "locationType", geography);
            }}
          />
        </Td>
        <Td>
          <LocationTag
            location={dataPoint.location}
            setLocation={(location: LocationType) => {
              editDataPoint(dataPoint.id, "location", location);
            }}
            geographyType={dataPoint.locationType}
          />
        </Td>
        <Td isNumeric>
          <ValueTag dataPointId={dataPoint.id} unit={dataPoint.valueUnit} />
        </Td>
        <Td>
          <UnitTag
            dataPointId={dataPoint.id}
            setUnit={(unit: string) => {
              editDataPoint(dataPoint.id, "valueUnit", unit);
            }}
          />
        </Td>
        <Td>
          <DataQualityTag
            dataQuality={dataPoint.dataQuality}
            setDataQuality={(dataQuality: string) => {
              editDataPoint(dataPoint.id, "dataQuality", dataQuality);
            }}
          />
        </Td>
        <Td>
          <YearTag
            singleYear={dataPoint.singleYearTimeframe}
            multiYear={dataPoint.multiYearTimeframe}
            setSingleYear={(singleYear?: number) => {
              editDataPoint(dataPoint.id, "singleYearTimeframe", singleYear);
            }}
            setMultiYear={(multiYear?: number[]) => {
              editDataPoint(dataPoint.id, "multiYearTimeframe", multiYear);
            }}
            yearType={yearType}
            setYearType={setYearType}
          />
        </Td>
      </Tr>
      {rowErrors && rowErrors.length > 0 && (
        <Tr>
          <Td colSpan={7}>
            <HStack spacing={2}>
              {rowErrors.map((error, idx) => (
                <HStack key={idx} bgColor="gray.100" p={2} borderRadius="md">
                  <WarningIcon color="red.500" />
                  <Text fontWeight="semibold">{error.message}</Text>
                </HStack>
              ))}
            </HStack>
          </Td>
        </Tr>
      )}
    </>
  );
};

export default DataPointRow;
