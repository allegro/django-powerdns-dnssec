import { it, describe, expect } from "@angular/core/testing";
import { LocalStorage } from "./local-storage";


describe("LocalStorageTest", () => {

  let testLocalStorage = new LocalStorage();

  it("set value should be the same of get", () => {
    testLocalStorage.set("key", "value");
    expect(testLocalStorage.get("key")).toBe("value");
  });

  it("set object value should be the same of get", () => {
    let obj = {key: "value"};
    testLocalStorage.setObject("key_object", obj);
    expect(testLocalStorage.getObject("key_object").key).toBe(obj.key);
  });

  it("remove key", () => {
    testLocalStorage.set("remove_key", "value");
    testLocalStorage.remove("remove_key");
    expect(testLocalStorage.get("remove_key")).toBe(false);
  });
});
