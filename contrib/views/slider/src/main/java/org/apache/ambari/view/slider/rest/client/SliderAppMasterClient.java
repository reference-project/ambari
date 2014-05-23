/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.ambari.view.slider.rest.client;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.commons.httpclient.HttpException;
import org.apache.log4j.Logger;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

public class SliderAppMasterClient extends BaseHttpClient {

	private static final Logger logger = Logger
	    .getLogger(SliderAppMasterClient.class);

	public static class SliderAppMasterData {
		public String registryUrl;
		public String uiUrl;
		public String managementUrl;
		public String publisherUrl;
	}

	public static class SliderAppContainerData {
		public String hostName;
		public String containerId;
	}

	public SliderAppMasterClient(String url) {
		super(url);
	}

	public SliderAppMasterData getAppMasterData() {
		try {
			String html = doGet("");
			int from = html.lastIndexOf("<ul>");
			int to = html.lastIndexOf("</ul>");
			if (from < to && from > -1) {
				SliderAppMasterData data = new SliderAppMasterData();
				String content = html.substring(from, to);
				content = content.replaceAll("<[^>]*>", "\r\n");
				String[] splits = content.split("\r\n");
				for (int i = 0; i < splits.length; i++) {
					String split = splits[i].trim();
					if ("Registry Web Service".equals(split))
						data.registryUrl = splits[i + 1].trim();
					else if ("Application Master Web UI".equals(split))
						data.uiUrl = splits[i + 1].trim();
					else if ("Management REST API".equals(split))
						data.managementUrl = splits[i + 1].trim();
					else if ("Publisher Service".equals(split))
						data.publisherUrl = splits[i + 1].trim();
				}
				return data;
			}
		} catch (HttpException e) {
			logger.warn("Unable to determine Ambari clusters", e);
			throw new RuntimeException(e.getMessage(), e);
		} catch (IOException e) {
			logger.warn("Unable to determine Ambari clusters", e);
			throw new RuntimeException(e.getMessage(), e);
		}
		return null;
	}

	public Map<String, String> getQuickLinks(String providerUrl) {
		try {
			JsonElement json = super.doGetJson(providerUrl, "/slider/quicklinks");
			Map<String, String> quickLinks = new HashMap<String, String>();
			JsonObject jsonObject = json.getAsJsonObject().get("entries")
			    .getAsJsonObject();
			for (Entry<String, JsonElement> entry : jsonObject.entrySet()) {
				if ("org.apache.slider.jmx".equals(entry.getKey())) {
					quickLinks.put("JMX", entry.getValue().getAsString());
				} else if ("org.apache.slider.monitor".equals(entry.getKey())) {
					quickLinks.put("UI", entry.getValue().getAsString());
				} else if ("org.apache.slider.metrics".equals(entry.getKey())) {
					quickLinks.put("Metrics", entry.getValue().getAsString());
				} else {
					quickLinks.put(entry.getKey(), entry.getValue().getAsString());
				}
			}
			return quickLinks;
		} catch (HttpException e) {
			logger.warn("Unable to determine quicklinks from " + providerUrl, e);
			throw new RuntimeException(e.getMessage(), e);
		} catch (IOException e) {
			logger.warn("Unable to determine quicklinks from " + providerUrl, e);
			throw new RuntimeException(e.getMessage(), e);
		}
	}

	public Map<String, Map<String, String>> getConfigs(String providerUrl) {
		try {
			Map<String, Map<String, String>> configsMap = new HashMap<String, Map<String, String>>();
			JsonElement json = super.doGetJson(providerUrl, "/slider");
			if (json != null) {
				JsonObject configsJson = json.getAsJsonObject().get("configurations")
				    .getAsJsonObject();
				for (Entry<String, JsonElement> entry : configsJson.entrySet()) {
					if ("complete-config".equals(entry.getKey())
					    || "quicklinks".equals(entry.getKey()))
						continue;
					JsonElement entryJson = super.doGetJson(providerUrl, "/slider/"
					    + entry.getKey());
					if (entryJson != null) {
						JsonObject configsObj = entryJson.getAsJsonObject().get("entries")
						    .getAsJsonObject();
						if (configsObj != null) {
							Map<String, String> configs = new HashMap<String, String>();
							for (Entry<String, JsonElement> e : configsObj.entrySet()) {
								configs.put(e.getKey(), e.getValue().getAsString());
							}
							configsMap.put(entry.getKey(), configs);
						}
					}
				}
			}
			return configsMap;
		} catch (HttpException e) {
			logger.warn("Unable to determine quicklinks from " + providerUrl, e);
			throw new RuntimeException(e.getMessage(), e);
		} catch (IOException e) {
			logger.warn("Unable to determine quicklinks from " + providerUrl, e);
			throw new RuntimeException(e.getMessage(), e);
		}
	}

	/**
	 * Provides only the interesting JMX metric names and values.
	 * 
	 * @param jmxUrl
	 * @return
	 */
	public Map<String, String> getJmx(String jmxUrl) {
		// TODO Mechanism to filter JMX beans to get only interesting metrics is
		// needed.
		return null;
	}

}