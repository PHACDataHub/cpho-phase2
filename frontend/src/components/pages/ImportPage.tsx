import { useMutation } from "@apollo/client";
import { AttachmentIcon } from "@chakra-ui/icons";
import {
  VStack,
  Input,
  Button,
  Heading,
  Center,
  Spinner,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { IMPORT_DATA } from "../../utils/graphql/mutations";
import { FileFormat, IndicatorType } from "../../utils/types";
import { FileTypeChoice } from "../organisms/FileTypeChoice";
import { Page } from "../template/Page";
import { v4 as uuidv4 } from "uuid";

export function ImportPage() {
  const [fileToUpload, setFileToUpload] = useState();

  const [activeType, setActiveType] = useState<FileFormat>("indicator");
  const [importData, { loading, error, data }] = useMutation(IMPORT_DATA);

  const [stage, setStage] = useState<"upload"|"review_schema"|"review_data">("upload");

  const [fileIndicators, setFileIndicators] = useState<IndicatorType[]>([]);

  const [customFieldMapping, setCustomFieldMapping] = useState<{[key: string]: string}>({});

  const handleFile = (event: any) => {
    event.preventDefault();
    const file = event.target.files[0];
    setFileToUpload(file);
  };

  const handleSubmit = async (event: any) => {
    event.preventDefault();
    if (fileToUpload) {
      try {
        await importData({
          variables: { file: fileToUpload },
        });
      } catch (error) {
        console.log(error);
      }
    }
  };

  const tryGetLocation = (cur: any) => {
    const loc = cur.location;
    if (loc) return loc;
  
    const field = prompt("Please enter the location field name", "location");
    if (field) {
      setCustomFieldMapping({ ...customFieldMapping, "location": field });
      return cur[field];
    }
  }

  /**
 * Takes a raw CSV string and converts it to a JavaScript object.
 * @param {string} text The raw CSV string.
 * @param {string[]} headers An optional array of headers to use. If none are
 * given, they are pulled from the first line of `text`.
 * @param {string} quoteChar A character to use as the encapsulating character.
 * @param {string} delimiter A character to use between columns.
 * @returns {object[]} An array of JavaScript objects containing headers as keys
 * and row entries as values.
 */
function csvToJson(text: string, headers?: string[], quoteChar = '"', delimiter = ',') {
  const regex = new RegExp(`(?<=,|\n|^)(?:"([^${quoteChar}]*)"|([^${delimiter}${quoteChar}\n]*))(?=${delimiter}|\n|$)`, 'gs');

  const match = (line: string | undefined) => line ? [...line.matchAll(regex)] : []
    .map(m => m[2])  // we only want the second capture group
    .slice(0, -1);   // cut off blank match at the end

  const lines = text.split('\n');
  const heads = headers ?? match(lines.shift());

  console.log(heads);

    return lines.map(line => {
      console.log(line);
      return match(line)?.reduce((acc, cur, i) => {
        const key = heads[i][0] ?? `extra_${i}`;
        return { ...acc, [key]: cur[0] };
      }, {});
    });
  }



  // useEffect(() => {
  //   if(stage==='review_schema'){
  //     (fileToUpload as any).text().then((text:string) => {
  //       const csvData = csvToJson(text);
        
  //       const indType = csvData.reduce((acc: IndicatorType[], cur: any) => {
  //         const ind = acc.find((ind) => ind.name === cur.indicator);
  //         if (ind) {
  //           ind.indicatordataSet.push({
  //             id: uuidv4(),
  //             indicatorId: ind.id,
  //             locationType: cur.locationType,
  //             location: customFieldMapping["location"] ? cur[customFieldMapping["location"]] : tryGetLocation(cur),
  //             sex: cur.sex,
  //             gender: cur.gender,
  //             ageGroup: cur.ageGroup,
  //             ageGroupType: cur.ageGroupType,
  //             dataQuality: cur.dataQuality,
  //             value: cur.value,
  //             valueLowerBound: cur.valueLowerBound,
  //             valueUpperBound: cur.valueUpperBound,
  //             valueUnit: cur.valueUnit,
  //             singleYearTimeframe: cur.singleYearTimeframe,
  //             multiYearTimeframe: cur.multiYearTimeframe,
  //           })
  //         } else if (cur.indicator) {
  //           const newInd: IndicatorType = {
  //             id: 0,
  //             name: cur.indicator,
  //             category: cur.category,
  //             subCategory: cur.subCategory,
  //             subIndicatorMeasurement: cur.subIndicatorMeasurement,
  //             detailedIndicator: cur.detailedIndicator,
  //             indicatordataSet: [{
  //               id: uuidv4(),
  //               locationType: cur.locationType,
  //               location: cur.location,
  //               sex: cur.sex,
  //               gender: cur.gender,
  //               ageGroup: cur.ageGroup,
  //               ageGroupType: cur.ageGroupType,
  //               dataQuality: cur.dataQuality,
  //               value: cur.value,
  //               valueLowerBound: cur.valueLowerBound,
  //               valueUpperBound: cur.valueUpperBound,
  //               valueUnit: cur.valueUnit,
  //               singleYearTimeframe: cur.singleYearTimeframe,
  //               multiYearTimeframe: cur.multiYearTimeframe,
  //             }]
  //           }

  //           acc.push(newInd);
  //         }

  //         return acc;
  //       }, [])
  //       setFileIndicators(indType);
  //     });
  //   }
  // }, [stage]);

  useEffect(() => {
    console.log(fileIndicators);
  }, [fileIndicators]);

  return (
    <Page title="Import File" backButton={{ show: true, redirectUrl: "/" }}>
      {stage==="upload" && <VStack align="flex-start" spacing={4}>
        <FileTypeChoice activeType={activeType} setActiveType={setActiveType} />
        <Center
          cursor={
            data?.importData?.success || activeType !== "indicator"
              ? "default"
              : "pointer"
          }
          backgroundColor="gray.100"
          _dark={{ backgroundColor: "gray.600" }}
          w="100%"
          py={8}
          onClick={() => document.getElementById("file_input")?.click()}
        >
          <Input
            id="file_input"
            display="none"
            name="uploaded_file"
            accept="text/csv"
            type="file"
            onChange={handleFile}
            disabled={activeType !== "indicator"}
          />
          {loading ? (
            <Spinner />
          ) : (
            <VStack
              color={activeType === "indicator" ? "initial" : "gray.400"}
              _dark={
                activeType === "indicator"
                  ? { color: "white" }
                  : { color: "gray.500" }
              }
            >
              {!data?.importData?.success && <AttachmentIcon boxSize="8" />}
              <Heading size="lg" fontWeight={600}>
                {data?.importData?.success
                  ? `Successfully uploaded ${(fileToUpload as any).name}`
                  : error
                  ? `Could not upload ${(fileToUpload as any).name}`
                  : fileToUpload
                  ? (fileToUpload as any).name
                  : activeType === "indicator"
                  ? "Click to select a file"
                  : `Import not available for ${
                      activeType === "benchmarking"
                        ? "Benchmarking"
                        : "Trend Analysis"
                    } yet`}
              </Heading>
            </VStack>
          )}
        </Center>

        <VStack w="100%" align="flex-end">
          <Button
            size="lg"
            fontSize={20}
            colorScheme="blue"
            onClick={() => setStage('review_schema')}
            isDisabled={!fileToUpload}
          >
            Review
          </Button>
        </VStack>
      </VStack>}

      {stage === 'review_schema' && <VStack align="flex-start" spacing={4}>
        <Heading size="lg" fontWeight={600}>
          Review Schema
        </Heading>
          
      </VStack>
      
      }
    </Page>
  );
}
