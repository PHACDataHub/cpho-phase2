import { Table, TableContainer, Tbody, Th, Thead, Tr } from "@chakra-ui/react";
import { DataPoint } from "../../utils/types";
import DataPointRow from "./DataPointRow";

export function DataPointTable({
  dataPoints,
  editDataPoint,
  replaceDataPoint,
  addDataPoint,
  deleteDataPoint,
  duplicateDataPoint,
}: {
  dataPoints: DataPoint[];
  editDataPoint: (uuid: string, field: string, value: any) => void;
  replaceDataPoint: (uuid: string, dataPoint: DataPoint) => void;
  addDataPoint: (dataPoint: DataPoint) => void;
  deleteDataPoint: (uuid: string) => void;
  duplicateDataPoint: (uuid: string) => void;
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
        <Tbody color="black">
          {dataPoints.map((dataPoint) => (
            <DataPointRow

              key={dataPoint.id}
              dataPoint={dataPoint}
              dataPoints={dataPoints}
              editDataPoint={editDataPoint}
              onDelete={() => deleteDataPoint(dataPoint.id)}
              onDuplicate={() => duplicateDataPoint(dataPoint.id)}
              replaceDataPoint={replaceDataPoint}
              addDataPoint={addDataPoint}
            />
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
}
