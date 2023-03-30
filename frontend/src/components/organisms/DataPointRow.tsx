import { CopyIcon, DeleteIcon, EditIcon } from "@chakra-ui/icons";
import {
  Tr,
  Td,
  HStack,
  IconButton,
  ButtonGroup,
  useDisclosure,
} from "@chakra-ui/react";
import { DataPoint, LocationType } from "../../utils/types";
import { AddDataPointModal } from "../molecules/AddDataPointModal";
import GeographyTag from "../atoms/dataPointTags/GeographyTag";
import LocationTag from "../atoms/dataPointTags/LocationTag";
import DataQualityTag from "../atoms/dataPointTags/DataQualityTag";
import YearTag from "../atoms/dataPointTags/YearTag";
import UnitTag from "../atoms/dataPointTags/UnitTag";
import ValueTag from "../atoms/dataPointTags/ValueTag";
import { useState } from "react";

const DataPointRow = ({
  dataPoint,
  dataPoints,
  editDataPoint,
  replaceDataPoint,
  addDataPoint,
  onDelete,
  onDuplicate,
}: {
  dataPoint: DataPoint;
  dataPoints: DataPoint[];
  editDataPoint: (id: string, field: string, value: any) => void;
  replaceDataPoint: (id: string, dataPoint: DataPoint) => void;
  addDataPoint: (dataPoint: DataPoint) => void;
  onDelete: (id: string) => void;
  onDuplicate: (id: string) => void;
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const idx = dataPoints.indexOf(dataPoint);

  const [yearType, setYearType] = useState<"SINGLE" | "RANGE">(
    dataPoint.multiYearTimeframe === undefined ? "SINGLE" : "RANGE"
  );

  return (
    <Tr
      key={idx}
      _hover={{
        bgColor: "gray.50",
        _dark: {
          bgColor: "blackAlpha.300",
        },
      }}
    >
      <Td isNumeric _dark={{ color: "white" }}>
        {idx + 1}
      </Td>
      <Td>
        <HStack spacing={2}>
          <ButtonGroup isAttached>
            <IconButton
              size="sm"
              aria-label="Delete Data Point"
              colorScheme="red"
              icon={<DeleteIcon />}
              onClick={() => onDelete(dataPoint.id)}
            />
            <IconButton
              size="sm"
              aria-label="Duplicate Data Point"
              colorScheme="blue"
              icon={<CopyIcon />}
              onClick={() => onDuplicate(dataPoint.id)}
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
        <GeographyTag
          type={dataPoint.geography}
          setGeography={(geography: string) => {
            editDataPoint(dataPoint.id, "geography", geography);
          }}
        />
      </Td>
      <Td>
        <LocationTag
          location={dataPoint.country}
          setLocation={(location: LocationType) => {
            editDataPoint(dataPoint.id, "country", location);
          }}
          geographyType={dataPoint.geography}
        />
      </Td>
      <Td isNumeric>
        <ValueTag
          value={dataPoint.value}
          setValue={(value: number) => {
            editDataPoint(dataPoint.id, "value", value);
          }}
        />
      </Td>
      <Td>
        <UnitTag
          unit={dataPoint.valueUnit}
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
  );
};

export default DataPointRow;
