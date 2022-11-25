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
import { v4 as uuidv4 } from "uuid";
import GeographyTag from "./tags/GeographyTag";
import LocationTag from "./tags/LocationTag";
import DataQualityTag from "./tags/DataQualityTag";
import YearTag from "./tags/YearTag";
import UnitTag from "./tags/UnitTag";
import ValueTag from "./tags/ValueTag";

const DataPointRow = ({
  dataPoint,
  dataPoints,
  setDataPoints,
}: {
  dataPoint: DataPoint;
  dataPoints: DataPoint[];
  setDataPoints: (dataPoints: DataPoint[]) => void;
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const idx = dataPoints.indexOf(dataPoint);

  const onDelete = () => {
    setDataPoints(dataPoints.slice(0, idx).concat(dataPoints.slice(idx + 1)));
  };

  const onDuplicate = () => {
    const newDataPoint: DataPoint = {
      ...dataPoint,
      uuid: uuidv4(),
    };
    setDataPoints(
      dataPoints
        .slice(0, idx + 1)
        .concat(newDataPoint, dataPoints.slice(idx + 1))
    );
  };

  const editDataPoint = (uuid: string, field: string, value: any) => {
    const newDataPoints = dataPoints.map((dataPoint) => {
      if (dataPoint.uuid === uuid) {
        if (field === "geography") {
          const country: LocationType =
            value === "COUNTRY"
              ? "CANADA"
              : value === "REGION"
              ? "ATLANTIC"
              : "AB";

          return {
            ...dataPoint,
            geography: value,
            country,
          };
        }
        return {
          ...dataPoint,
          [field]: value,
        };
      }
      return dataPoint;
    });
    setDataPoints(newDataPoints);
  };

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
          dataPoints={dataPoints}
          setDataPoints={setDataPoints}
          isOpen={isOpen}
          onClose={onClose}
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
        <ValueTag value={dataPoint.value} />
      </Td>
      <Td>
        <UnitTag unit={dataPoint.valueUnit} />
      </Td>
      <Td>
        <DataQualityTag dataQuality={dataPoint.dataQuality} />
      </Td>
      <Td>
        <YearTag
          year={dataPoint.singleYearTimeframe ?? dataPoint.multiYearTimeframe!}
        />
      </Td>
    </Tr>
  );
};

export default DataPointRow;
