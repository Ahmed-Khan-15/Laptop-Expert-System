# decision_tree.py
# The DECISION TREE for guided diagnosis.
# Every question node has:  "question", "yes" and "no" (the next nodes)
# and optionally "yes_adds" / "no_adds" (symptoms recorded for that answer).
# Every end node (leaf) has: "result" (the conclusion) and "category".


def leaf(result, category):
    """Create an end node of the tree."""
    return {"result": result, "category": category}


DECISION_TREE = {
    "question": "Does the laptop show any sign of power (lights or fan noise)?",
    # ---------- NO POWER ----------
    "no_adds": ["no_lights", "no_fan_sound"],
    "no": {
        "question": "Is the charger plugged into a working outlet?",
        "yes_adds": ["charger_plugged"],
        "yes": leaf("Power problem: the charger/outlet may be faulty or the battery is dead.", "Power & Boot"),
        "no": leaf("Plug in the charger and wait 15-20 minutes, then try again.", "Power & Boot"),
    },
    # ---------- HAS POWER ----------
    "yes_adds": ["power_light_on"],
    "yes": {
        "question": "Does anything appear on the screen?",
        # ----- Screen is blank -----
        "no_adds": ["no_display"],
        "no": {
            "question": "Does an external monitor show the display correctly?",
            "yes_adds": ["external_monitor_works"],
            "yes": leaf("The laptop screen or its cable is probably faulty.", "Power & Boot"),
            "no": {
                "question": "Do you hear beeping sounds at startup?",
                "yes_adds": ["beeping_sound"],
                "yes": leaf("Beeps usually point to a RAM problem.", "Power & Boot"),
                "no": leaf("Display or graphics problem is likely.", "Power & Boot"),
            },
        },
        # ----- Screen works -----
        "yes": {
            "question": "Does the laptop reach the login screen / desktop?",
            # ----- Cannot boot -----
            "no": {
                "question": "Do you see a 'No bootable device' or 'OS not found' error?",
                "yes_adds": ["no_bootable_device_error"],
                "yes": leaf("The boot drive is not detected or the boot order is wrong.", "Power & Boot"),
                "no": {
                    "question": "Does the laptop restart again and again (boot loop)?",
                    "yes_adds": ["boot_loop"],
                    "yes": {
                        "question": "Did this start right after an update?",
                        "yes_adds": ["recent_update"],
                        "yes": leaf("A corrupted update is likely the cause.", "Power & Boot"),
                        "no": leaf("A boot loop without an update: check the OS and drive health.", "Power & Boot"),
                    },
                    "no": {
                        "question": "Is it stuck on the manufacturer logo for a very long time?",
                        "yes_adds": ["stuck_on_logo", "very_long_boot"],
                        "yes": leaf("OS corruption or a failing drive is possible.", "Power & Boot"),
                        "no": leaf("Boot problem with unclear cause: check BIOS and the drive.", "Power & Boot"),
                    },
                },
            },
            # ----- Boots fine: find the problem area -----
            "yes": {
                "question": "Is the problem related to the internet or Wi-Fi?",
                "yes": {
                    "question": "Are you connected to Wi-Fi but have no internet?",
                    "yes_adds": ["wifi_connected_no_internet"],
                    "yes": {
                        "question": "Do your other devices also have no internet?",
                        "yes_adds": ["other_devices_no_internet"],
                        "no_adds": ["other_devices_work"],
                        "yes": leaf("The router or internet provider is likely the problem.", "Networking"),
                        "no": leaf("The problem is on this laptop (IP/DNS settings).", "Networking"),
                    },
                    "no": {
                        "question": "Can you see no Wi-Fi networks at all?",
                        "yes_adds": ["no_wifi_networks_found"],
                        "yes": leaf("The Wi-Fi adapter is disabled or its driver is broken.", "Networking"),
                        "no": {
                            "question": "Is the internet slow?",
                            "yes_adds": ["slow_internet"],
                            "yes": {
                                "question": "Are other devices also slow?",
                                "yes_adds": ["other_devices_also_slow"],
                                "no_adds": ["other_devices_fine"],
                                "yes": leaf("The router or internet provider is likely slow.", "Networking"),
                                "no": leaf("Something on this laptop is slowing the internet.", "Networking"),
                            },
                            "no": {
                                "question": "Does the Wi-Fi keep disconnecting?",
                                "yes_adds": ["wifi_drops"],
                                "yes": leaf("Wi-Fi signal or driver problem.", "Networking"),
                                "no": leaf("Another network problem: check the connection details.", "Networking"),
                            },
                        },
                    },
                },
                "no": {
                    "question": "Is the problem related to the battery or charging?",
                    "yes": {
                        "question": "Is the laptop not charging when plugged in?",
                        "yes_adds": ["not_charging"],
                        "yes": {
                            "question": "Is the charger's light on?",
                            "yes_adds": ["charger_light_on"],
                            "no_adds": ["charger_light_off"],
                            "yes": leaf("Battery, charging port or driver problem.", "Battery & Charging"),
                            "no": leaf("The charger is probably faulty.", "Battery & Charging"),
                        },
                        "no": {
                            "question": "Does the battery drain very fast?",
                            "yes_adds": ["fast_battery_drain"],
                            "yes": {
                                "question": "Is the laptop more than 3 years old?",
                                "yes_adds": ["laptop_over_3_years"],
                                "yes": leaf("The battery is probably worn out.", "Battery & Charging"),
                                "no": leaf("Background apps may be draining the battery.", "Battery & Charging"),
                            },
                            "no": {
                                "question": "Does the battery look swollen or bulging?",
                                "yes_adds": ["battery_swollen"],
                                "yes": leaf("DANGER: swollen battery. Stop using the laptop.", "Battery & Charging"),
                                "no": leaf("Another battery issue: check battery health.", "Battery & Charging"),
                            },
                        },
                    },
                    "no": {
                        "question": "Is the laptop slow, freezing or very hot?",
                        "yes": {
                            "question": "Is it very hot, or is the fan very loud?",
                            "yes_adds": ["overheating", "loud_fan"],
                            "no_adds": ["slow_overall"],
                            "yes": leaf("Cooling problem (dust, fan or thermal paste).", "Hardware"),
                            "no": {
                                "question": "Is disk usage near 100%?",
                                "yes_adds": ["disk_usage_100_percent"],
                                "yes": leaf("The disk is the bottleneck.", "Storage"),
                                "no": leaf("A general performance problem (RAM, startup programs).", "Performance"),
                            },
                        },
                        "no": {
                            "question": "Do pop-up ads keep appearing or did your homepage change?",
                            "yes_adds": ["popups_appearing", "homepage_changed"],
                            "yes": leaf("Adware or a browser hijacker is likely.", "Security"),
                            "no": leaf("A software or OS problem (crashes, updates, drivers).", "Software & OS"),
                        },
                    },
                },
            },
        },
    },
}


def follow_path(path):
    """Walk the tree using the list of answers ("yes"/"no") given so far.
    Returns: the current node, the symptoms collected, and the list of steps taken."""
    node = DECISION_TREE
    symptoms = []
    steps = []
    for answer in path:
        steps.append((node["question"], answer))
        extra = node.get(answer + "_adds", [])
        for symptom in extra:
            symptoms.append(symptom)
        node = node[answer]
    return node, symptoms, steps


def is_leaf(node):
    """A leaf (end node) has a result instead of a question."""
    return "result" in node
