import { Button, Heading, ButtonGroup } from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";
import { IndicatorType } from "../../utils/types";
import { Page } from "../template/Page";
import { FileColumnData } from "../../utils/constants";
import FileUpload from "../organisms/FileUpload";
import FileReviewSchema from "../organisms/FileReviewSchema";
import { v4 as uuidv4 } from "uuid";
import IndicatorForm from "../organisms/IndicatorForm";
import { useMutation } from "@apollo/client";
import { CREATE_INDICATOR } from "../../utils/graphql/mutations";

export function ImportPage() {
  const [fileToUpload, setFileToUpload] = useState<File>();
  const [fileText, setFileText] = useState<string>("");

  const [stage, setStage] = useState<
    "upload" | "review_schema" | "review_data"
  >("upload");

  const [fileIndicators, setFileIndicators] = useState<IndicatorType[]>([]);
  const [fileHeaders, setFileHeaders] = useState<string[]>([]);

  const [fieldMapping, setFieldMapping] = useState<{
    [key: string]: string;
  }>({
    indicatorName: "",
    category: "",
    subCategory: "",
    detailedIndicator: "",
    subIndicatorMeasurement: "",
    locationType: "",
    location: "",
    sex: "",
    gender: "",
    ageGroup: "",
    ageGroupType: "",
    dataQuality: "",
    value: "",
    valueLowerBound: "",
    valueUpperBound: "",
    valueUnit: "",
    singleYearTimeFrame: "",
    multiYearTimeFrame: "",
  });

  const csvToJson = useCallback(
    (text: string, headers?: string[], quoteChar = '"', delimiter = ",") => {
      const regex = new RegExp(
        `(?<=,|\n|^)(?:"([^${quoteChar}]*)"|([^${delimiter}${quoteChar}\n]*))(?=${delimiter}|\n|$)`,
        "gs"
      );

      const match = (line: string | undefined) =>
        line
          ? [...line.matchAll(regex)]
          : []
              .map((m) => m[2]) // we only want the second capture group
              .slice(0, -1); // cut off blank match at the end

      const lines = text.split("\n");
      const heads = headers ?? match(lines.shift());

      return lines.map((line) => {
        return match(line)?.reduce((acc, cur, i) => {
          const key =
            Object.entries(fieldMapping).find(([key, value]) => {
              return value === heads[i][0];
            })?.[0] || `custom_${i}`;
          return { ...acc, [key]: cur[1] ?? cur[0] };
        }, {});
      });
    },
    [fieldMapping]
  );

  const csvHeaders = (text: string, quoteChar = '"', delimiter = ",") => {
    const regex = new RegExp(
      `(?<=,|\n|^)(?:"([^${quoteChar}]*)"|([^${delimiter}${quoteChar}\n]*))(?=${delimiter}|\n|$)`,
      "gs"
    );

    const match = (line: string | undefined) =>
      line
        ? [...line.matchAll(regex)]
        : []
            .map((m) => m[2]) // we only want the second capture group
            .slice(0, -1); // cut off blank match at the end

    const lines = text.split("\n");
    const headers = match(lines.shift());
    return headers.map((header) => header[0]); // we only want the regex match string
  };

  useEffect(() => {
    if (fileToUpload) {
      (fileToUpload as any).text().then((text: string) => {
        setFileText(text);
      });
    }
  }, [fileToUpload]);

  useEffect(() => {
    if (stage === "review_schema" && fileText && fileHeaders.length === 0) {
      const csvFileHeaders = csvHeaders(fileText);
      console.log(csvFileHeaders);
      setFileHeaders(csvFileHeaders);
    } else if (stage === "review_data") {
      const csvData = csvToJson(fileText);

      console.log(csvData);

      const indType = csvData.reduce((acc: IndicatorType[], cur: any) => {
        const ind = acc.find((ind) => ind.name === cur.indicatorName);
        if (ind) {
          ind.indicatordataSet.push({
            id: uuidv4(),
            indicatorId: ind.id,
            locationType: cur.locationType,
            location: cur.location,
            sex: cur.sex,
            gender: cur.gender,
            ageGroup: cur.ageGroup,
            ageGroupType: cur.ageGroupType,
            dataQuality: cur.dataQuality,
            value: cur.value,
            valueLowerBound: cur.valueLowerBound,
            valueUpperBound: cur.valueUpperBound,
            valueUnit: cur.valueUnit,
            singleYearTimeframe: cur.singleYearTimeframe,
            multiYearTimeframe: cur.multiYearTimeframe,
          });
        } else if (cur.indicatorName) {
          const newInd: IndicatorType = {
            id: 0,
            name: cur.indicatorName,
            category: cur.category,
            subCategory: cur.subCategory,
            subIndicatorMeasurement: cur.subIndicatorMeasurement,
            detailedIndicator: cur.detailedIndicator,
            indicatordataSet: [
              {
                id: uuidv4(),
                locationType: cur.locationType,
                location: cur.location,
                sex: cur.sex,
                gender: cur.gender,
                ageGroup: cur.ageGroup,
                ageGroupType: cur.ageGroupType,
                dataQuality: cur.dataQuality,
                value: cur.value,
                valueLowerBound: cur.valueLowerBound,
                valueUpperBound: cur.valueUpperBound,
                valueUnit: cur.valueUnit,
                singleYearTimeframe: cur.singleYearTimeframe,
                multiYearTimeframe: cur.multiYearTimeframe,
              },
            ],
          };

          acc.push(newInd);
        }

        return acc;
      }, []);
      setFileIndicators(indType);
    }
  }, [stage, fileToUpload, fieldMapping, fileHeaders, fileText, csvToJson]);

  useEffect(() => {
    if (fileHeaders) {
      console.log("file headers");
      fileHeaders.forEach((header) => {
        console.log("looking for", header);
        FileColumnData.indicator.forEach((column) => {
          if (column.matches?.includes(header.toLowerCase())) {
            console.log("found", header, "for", column.value);
            setFieldMapping((fieldMapping) => ({
              ...fieldMapping,
              [column.value]: header,
            }));
          }
        });
      });
    }
  }, [fileHeaders]);

  useEffect(() => {
    console.log(fileIndicators);
  }, [fileIndicators]);

  const [indicatorStep, setIndicatorStep] = useState(0);
  const [submittedIndicatorIndexes, setSubmittedIndicatorIndexes] = useState<
    number[]
  >([]);

  const [createIndicator, { loading, error, data }] =
    useMutation(CREATE_INDICATOR);

  return (
    <Page title="Import File" backButton={{ show: true, redirectUrl: "/" }}>
      {stage === "upload" && (
        <FileUpload
          fileToUpload={fileToUpload}
          setFileToUpload={setFileToUpload}
          setStage={setStage}
          data={data}
          loading={loading}
          error={error}
        />
      )}

      {stage === "review_schema" && (
        <FileReviewSchema
          fieldMapping={fieldMapping}
          setFieldMapping={setFieldMapping}
          fileHeaders={fileHeaders}
          setStage={setStage}
        />
      )}

      {stage === "review_data" && (
        <>
          <Heading>Review Data for {fileIndicators.length} indicators</Heading>
          <ButtonGroup>
            {fileIndicators.map((indicator, idx) => (
              <Button
                key={idx}
                onClick={() => setIndicatorStep(idx)}
                isActive={indicatorStep === idx}
                isDisabled={submittedIndicatorIndexes.includes(idx)}
              >
                {indicator.name}
              </Button>
            ))}
          </ButtonGroup>
          {fileIndicators.map(
            (indicator, idx) =>
              idx === indicatorStep && (
                <>
                  <IndicatorForm indicator={indicator} mode="create" />
                </>
              )
          )}
        </>
      )}
    </Page>
  );
}
