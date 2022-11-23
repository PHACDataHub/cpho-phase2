import { CopyIcon, DeleteIcon, EditIcon } from "@chakra-ui/icons";
import {
  Tr,
  Td,
  HStack,
  IconButton,
  ButtonGroup,
  useDisclosure,
} from "@chakra-ui/react";
import { DataPoint } from "../../../utils/types";
import { AddDataPointModal } from "./AddDataPointModal";

const DataPointRow = ({
  dataPoint,
  dataPoints,
  setDataPoints,
  idx,
}: {
  dataPoint: DataPoint;
  dataPoints: DataPoint[];
  setDataPoints: (dataPoints: DataPoint[]) => void;
  idx: number;
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const onDelete = () => {
    setDataPoints(dataPoints.slice(0, idx).concat(dataPoints.slice(idx + 1)));
  };

  const onDuplicate = () => {
    setDataPoints(
      dataPoints.slice(0, idx + 1).concat(dataPoint, dataPoints.slice(idx + 1))
    );
  };

  const isDuplicate = (() => {
    let result = [];

    dataPoints.forEach((dp, idx) => {
      if (dp === dataPoint) {
        result.push(idx);
      }
    });

    return result.length > 1;
  })();

  return (
    <>
      <Tr
        key={idx}
        _hover={{
          bgColor: isDuplicate ? "red.200" : "gray.100",
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
        </Td>
        <Td>{dataPoint.geography}</Td>
        <Td>{dataPoint.country}</Td>
        <Td isNumeric>
          {dataPoint.value}
          {dataPoint.valueUnit === "PERCENT" ? " %" : ""}
        </Td>
        <Td>{dataPoint.dataQuality}</Td>
        <Td>{dataPoint.singleYearTimeframe ?? dataPoint.multiYearTimeframe}</Td>
      </Tr>
      <AddDataPointModal
        dataPointIdx={idx}
        dataPoints={dataPoints}
        setDataPoints={setDataPoints}
        isOpen={isOpen}
        onClose={onClose}
      />
    </>
  );
};

export default DataPointRow;
