import {
  Table,
  TableCaption,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { DataPoint } from "../../utils/types";

const DataPointDisplay = ({ dataPoints }: { dataPoints: DataPoint[] }) => {
  return (
    <TableContainer>
      <Table variant="simple">
        <TableCaption></TableCaption>
        <Thead>
          <Tr>
            <Th isNumeric>#</Th>
            <Th>Geography</Th>
            <Th>Location</Th>
            <Th isNumeric>Value</Th>
            <Th>Unit</Th>
            <Th>Data Quality</Th>
            <Th>Year</Th>
          </Tr>
        </Thead>
        <Tbody>
          {dataPoints.map((dataPoint, idx) => (
            <Tr key={dataPoint.id}>
              <Td isNumeric>{idx + 1}</Td>
              <Td>{dataPoint.location}</Td>
              <Td>{dataPoint.locationType}</Td>
              <Td isNumeric>{dataPoint.value}</Td>
              <Td>{dataPoint.valueUnit}</Td>
              <Td>{dataPoint.dataQuality}</Td>
              <Td>
                {dataPoint.singleYearTimeframe ?? dataPoint.multiYearTimeframe}
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

export default DataPointDisplay;
