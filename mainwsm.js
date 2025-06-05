importScripts('/scripts/pkg7/deportes.worker.js');

async function createModule() {
    self.wasmModule = await Module();
    self.postMessage({ type: 'ready' });
}

window.DEPORTESdecode = async (msg) => {
    const { inputData, messageId, type } = msg.data;
    const chunkSize = 8192;

    if (!self.wasmModule) {
        await createModule();
    }

    if (type === 'de-portes') {
        if (!inputData) {
            self.postMessage({ error: "Missing input data" });
            return;
        }

        let offset = 0,
            currentPointer = 0,
            result = new Uint8Array(inputData.byteLength);

        while (offset < inputData.byteLength) {
            let inputArray = new Uint8Array(inputData);

            const chunk = inputArray.subarray(offset, offset + chunkSize);

            const ptr = self.wasmModule._malloc(chunk.length);
            self.wasmModule.HEAPU8.set(chunk, ptr);

            const resultPtr = self.wasmModule._Deportes4(ptr, chunk.length);

            const subarrayResult = self.wasmModule.HEAPU8.subarray(resultPtr, resultPtr + chunk.length - 1);
            result.set(subarrayResult, currentPointer);
            currentPointer += subarrayResult.length;

            self.wasmModule._free(ptr);
            self.wasmModule._free(resultPtr);

            offset += chunkSize;
        }

        return result.subarray(0, currentPointer);
    }
};


self.onmessage = async (msg) => {
    const { inputData, messageId, type } = msg.data;
    const chunkSize = 8192;

    if (!self.wasmModule) {
        await createModule();
    }

    if (type === 'de-portes') {
        if (!inputData) {
            self.postMessage({ error: "Missing input data" });
            return;
        }

        let offset = 0,
            currentPointer = 0,
            result = new Uint8Array(inputData.byteLength);

        while (offset < inputData.byteLength) {
            let inputArray = new Uint8Array(inputData);

            const chunk = inputArray.subarray(offset, offset + chunkSize);

            const ptr = self.wasmModule._malloc(chunk.length);
            self.wasmModule.HEAPU8.set(chunk, ptr);

            const resultPtr = self.wasmModule._Deportes4(ptr, chunk.length);

            const subarrayResult = self.wasmModule.HEAPU8.subarray(resultPtr, resultPtr + chunk.length - 1);
            result.set(subarrayResult, currentPointer);
            currentPointer += subarrayResult.length;

            self.wasmModule._free(ptr);
            self.wasmModule._free(resultPtr);

            offset += chunkSize;
        }

        postMessage({ messageId, type: "portes", outputData: result.subarray(0, currentPointer) });
    }
};
