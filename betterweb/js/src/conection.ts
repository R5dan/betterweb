// @ts-expect-error ZOD is installed as a module
import { z } from "https://unpkg.com/zod@3.25.67/v3/index.js";
// import {z} from "zod"

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
	function: (data) => (document.body.innerHTML = data),
});

processes.add({
	type: "ls",
	data: z.union([
		z.object({
			type: z.literal("get"),
		}),
		z.object({
			type: z.literal("set"),
			data: z.object({
				key: z.string(),
				value: z.string(),
			}),
		}),
	]),
	function: (data) => {
		if (data.type === "get") {
			socket.send(
				JSON.stringify({
					type: "ls-receive",
					data: localStorage,
				})
			);
		} else if (data.type === "set") {
			localStorage.setItem(data.data.key, data.data.value);
		}
	},
});

processes.add({
	type: "router",
	data: z.union([
		z.object({
			type: z.literal("push"),
			url: z.string(),
			client: z.boolean(),
		}),
		z.object({
			type: z.literal("replace"),
			url: z.string(),
			client: z.boolean(),
		}),
		z.object({ type: z.literal("reload"), client: z.boolean() }),
		z.object({ type: z.literal("back") }),
		z.object({ type: z.literal("forward") }),
	]),
	function: (data) => {
		if (data.type === "push") {
			if (data.client) {
				history.pushState({}, "", data.url);
			} else {
				window.location.href = data.url;
			}
		} else if (data.type === "replace") {
			if (data.client) {
				history.replaceState({}, "", data.url);
			} else {
				window.location.replace(data.url);
			}
		} else if (data.type === "back") {
			history.back();
		} else if (data.type === "forward") {
			history.forward();
		} else if (data.type === "reload") {
			if (data.client) {
				sendRouteUpdate();
			} else {
				window.location.reload();
			}
		}
	},
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
			data: getUrlData(),
		})
	);
};

// @ts-expect-error Assigning value
window.socket = socket;

// --- Router Implementation ---
function getUrlData() {
	return {
		url: document.location.pathname,
		query: Object.fromEntries(
			new URLSearchParams(document.location.search)
		),
		hash: document.location.hash.slice(1),
	};
}

function sendRouteUpdate() {
	socket.send(
		JSON.stringify({
			type: "request",
			data: getUrlData(),
		})
	);
}

// Monkey-patch pushState and replaceState to notify server
(function () {
	const origPushState = history.pushState;
	const origReplaceState = history.replaceState;

	history.pushState = function (...args) {
		origPushState.apply(this, args);
		sendRouteUpdate();
		window.dispatchEvent(new Event("bw:navigate"));
	};
	history.replaceState = function (...args) {
		origReplaceState.apply(this, args);
		sendRouteUpdate();
		window.dispatchEvent(new Event("bw:navigate"));
	};

	window.addEventListener("popstate", () => {
		sendRouteUpdate();
		window.dispatchEvent(new Event("bw:navigate"));
	});
})();

// Expose router methods
export const router = {};

// Optionally, attach router to window for debugging
// @ts-expect-error
window.bwRouter = router;
