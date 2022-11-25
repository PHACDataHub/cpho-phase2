import { CopyIcon, DeleteIcon, EditIcon } from "@chakra-ui/icons";
import {
  Tr,
  Td,
  HStack,
  IconButton,
  ButtonGroup,
  useDisclosure,
} from "@chakra-ui/react";
import { DataPoint, LocationType } from "../../../../utils/types";
import { AddDataPointModal } from "../AddDataPointModal";
import GeographyTag from "./tags/GeographyTag";
import LocationTag from "./tags/LocationTag";
import DataQualityTag from "./tags/DataQualityTag";
import YearTag from "./tags/YearTag";
import UnitTag from "./tags/UnitTag";
import ValueTag from "./tags/ValueTag";
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
  editDataPoint: (uuid: string, field: string, value: any) => void;
  replaceDataPoint: (uuid: string, dataPoint: DataPoint) => void;
  addDataPoint: (dataPoint: DataPoint) => void;
  onDelete: (uuid: string) => void;
  onDuplicate: (uuid: string) => void;
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
      }}
      bgColor="white"
    >
      <Td isNumeric>{idx + 1}</Td>
      <Td>
        <HStack spacing={2}>
          <ButtonGroup isAttached>
            <IconButton
              size="sm"
              aria-label="Delete Data Point"
              colorScheme="red"
              icon={<DeleteIcon />}
              onClick={() => onDelete(dataPoint.uuid)}
            />
            <IconButton
              size="sm"
              aria-label="Duplicate Data Point"
              colorScheme="blue"
              icon={<CopyIcon />}
              onClick={() => onDuplicate(dataPoint.uuid)}
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
            editDataPoint(dataPoint.uuid, "geography", geography);
          }}
        />
      </Td>
      <Td>
        <LocationTag
          location={dataPoint.country}
          setLocation={(location: LocationType) => {
            editDataPoint(dataPoint.uuid, "country", location);
          }}
          geographyType={dataPoint.geography}
        />
      </Td>
      <Td isNumeric>
        <ValueTag
          value={dataPoint.value}
          setValue={(value: number) => {
            editDataPoint(dataPoint.uuid, "value", value);
          }}
        />
      </Td>
      <Td>
        <UnitTag
          unit={dataPoint.valueUnit}
          setUnit={(unit: string) => {
            editDataPoint(dataPoint.uuid, "valueUnit", unit);
          }}
        />
      </Td>
      <Td>
        <DataQualityTag
          dataQuality={dataPoint.dataQuality}
          setDataQuality={(dataQuality: string) => {
            editDataPoint(dataPoint.uuid, "dataQuality", dataQuality);
          }}
        />
      </Td>
      <Td>
        <YearTag
          singleYear={dataPoint.singleYearTimeframe}
          multiYear={dataPoint.multiYearTimeframe}
          setSingleYear={(singleYear?: number) => {
            editDataPoint(dataPoint.uuid, "singleYearTimeframe", singleYear);
          }}
          setMultiYear={(multiYear?: number[]) => {
            editDataPoint(dataPoint.uuid, "multiYearTimeframe", multiYear);
          }}
          yearType={yearType}
          setYearType={setYearType}
        />
      </Td>
    </Tr>
  );
};

export default DataPointRow;
