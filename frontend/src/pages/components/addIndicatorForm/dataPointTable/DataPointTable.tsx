import { Table, TableContainer, Tbody, Th, Thead, Tr } from "@chakra-ui/react";
import { DataPoint } from "../../../../utils/types";
import DataPointRow from "./DataPointRow";

export function DataPointTable({
  dataPoints,
  setDataPoints,
}: {
  dataPoints: DataPoint[];
  setDataPoints: (dataPoints: DataPoint[]) => void;
}) {
  return (
    <TableContainer w={["100%", "95%", "90%", "85%", "75%"]}>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th isNumeric>#</Th>
            <Th>Actions</Th>
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
            <DataPointRow
              key={dataPoint.uuid}
              dataPoint={dataPoint}
              dataPoints={dataPoints}
              setDataPoints={setDataPoints}
            />
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
}
