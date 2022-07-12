import { VStack, Text, Box, FormControl, FormLabel, Input, Button } from "@chakra-ui/react";
import { useState } from "react";
import { ColorModeSwitcher } from "../ColorModeSwitcher";
import { Page } from "./Page";

export function ImportPage() {

  const [fileToUpload, setFileToUpload] = useState();
  const [status, setStatus] = useState<'idle' | 'loading' | 'failure' | 'success'>('idle');

  const handleFile = (event: any) => {
    event.preventDefault();
    const file = event.target.files[0];
    setFileToUpload(file);
    console.log("GOT IT!", file)
  }

  const handleSubmit = (event: any) => {
    event.preventDefault();
    let formData = new FormData();
    if (fileToUpload) {
      formData.append('file', fileToUpload);
      console.log("Submit")
      if (fileToUpload) {
        fetch(process.env.REACT_APP_SERVER_URL || 'http://localhost:8000/api/import', {
          method: 'POST',
          body: formData,
          mode: 'no-cors',
          credentials: 'include',
        }).then((res) => console.log(res))
      }
    }
  }

  return (
    <Page
      title="Import File"
      backButton={{ show: true, redirectUrl: "/" }}
    >
      <Input accept="text/csv" type="file" onChange={handleFile} />
      <Button onClick={handleSubmit}>Import</Button>
    </Page>
  );
}
