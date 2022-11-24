import { CopyIcon, DeleteIcon, EditIcon } from "@chakra-ui/icons";
import {
  Tr,
  Td,
  HStack,
  IconButton,
  ButtonGroup,
  useDisclosure,
} from "@chakra-ui/react";
import { DataPoint } from "../../../../utils/types";
import { AddDataPointModal } from "../AddDataPointModal";
import { v4 as uuidv4 } from "uuid";
import GeographyTag from "./tags/GeographyTag";
import LocationTag from "./tags/LocationTag";
import DataQualityTag from "./tags/DataQualityTag";
import YearTag from "./tags/YearTag";

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

  const isDuplicate = (() => {
    let result = [];

    dataPoints.forEach((dp, idx) => {
      const { uuid, ...dpRest } = dp;
      const { uuid: uuid2, ...dataPointRest } = dataPoint;
      if (dpRest === dataPointRest) {
        result.push(idx);
      }
    });

    return result.length > 1;
  })();

  return (
    <Tr
      key={idx}
      _hover={{
        bgColor: isDuplicate ? "red.200" : "gray.50",
      }}
      bgColor={isDuplicate ? "red.100" : "white"}
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
          dataPointUuid={dataPoint.uuid}
          dataPoints={dataPoints}
          setDataPoints={setDataPoints}
          isOpen={isOpen}
          onClose={onClose}
        />
      </Td>
      <Td>
        <GeographyTag type={dataPoint.geography} />
      </Td>
      <Td>
        <LocationTag location={dataPoint.country} />
      </Td>
      <Td isNumeric>{dataPoint.value}</Td>
      <Td>{dataPoint.valueUnit === "PERCENT" ? " %" : ""}</Td>
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
