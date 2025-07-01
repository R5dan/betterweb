// @ts-expect-error ZOD is installed as a module
import { z } from "https://unpkg.com/zod@3.25.67/v3/index.js";

const socket = new WebSocket("ws://localhost:8000/__bw/ws");

type Process<T extends z.ZodSchema> = {
	type: string;
	data: T;
	function: (data: z.infer<T>) => void;
};

const ZodSchema = z.custom<z.ZodSchema>((val) => val instanceof z.ZodSchema);

const Process = z.object({
	type: z.string(),
	data: ZodSchema,
	function: z.function(),
});

const ProcessJSON = z.object({
	type: z.string(),
	data: ZodSchema,
});

class Processes {
	private processes: Process<any>[] = [];

	public add<T extends z.ZodSchema>(process: Process<T>) {
		this.processes.push(process);
	}

	public remove<T extends z.ZodSchema>(process: Process<T>) {
		this.processes = this.processes.filter((p) => p !== process);
	}

	public run<T extends z.ZodSchema>(process: Process<T>, data: T) {
		process.function(data);
	}

	public runNamed<T extends any>(name: string, data: T) {
		const proc = this.processes.filter((p) => p.type === name);
		proc.forEach((p) => this.run(p, data));
	}
}

const processes = new Processes();

processes.add({
	type: "console",
	data: z.object({
		type: z.union([
			z.literal("log"),
			z.literal("error"),
			z.literal("warn"),
			z.literal("info"),
		]),
		message: z.string(),
	}),
	function: ({ type, message }) => {
		if (type === "log") {
			console.log(message);
		} else if (type === "error") {
			console.error(message);
		} else if (type === "info") {
			console.info(message);
		} else if (type === "warn") {
			console.warn(message);
		}
	},
});

processes.add({
	type: "console-clear",
	data: z.null(),
	function: console.clear,
});

processes.add({
	type: "html",
	data: z.string(),
	function: (data) => document.body.innerHTML = data,
});

socket.onmessage = async (event) => {
	const json = JSON.parse(await (event.data as Blob).text());

	// const processed = ProcessJSON.parse(json);
	processes.runNamed(json.type, json.data);
};

socket.onopen = () => {
	socket.send(
		JSON.stringify({
			type: "request",
			data: {
				url: document.location.pathname,
				query: new URLSearchParams(document.location.search),
				hash: document.location.hash.slice(1),
			},
		})
	);
};

window.socket = socket;
