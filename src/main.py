import asyncio
import math
from colorama import init, Fore, Back, Style
from wizwalker import ClientHandler
from wizwalker.memory.memory_objects.camera_controller import ElasticCameraController, CameraController
from wizwalker.errors import HookNotActive
from wizwalker import Client, utils, Orient, XYZ
import random
import os

path_file = "path.txt"

if os.path.exists(path_file):
    # Read the existing path from path.txt
    with open(path_file, "r") as file:
        wiz_path = file.read()
else:
    # Ask for the Wizard101 path
    wiz_path = input(Fore.YELLOW + "Paste your Wizard101 file path:\n" + Fore.WHITE)

    # Create path.txt and write the path to it
    with open(path_file, "w") as file:
        file.write(wiz_path)

utils.override_wiz_install_location(rf'{wiz_path}') # Enter your wizard101 path.
print(Fore.GREEN + "Path set to " + Fore.WHITE + wiz_path + Style.DIM + " Change in path.txt if needed" + Style.RESET_ALL)

init() #for logging

# DO NOT TOUCH ANYTHING IN THE DASHES -----------------------------------------------------

def calc_Distance(xyz_1 : XYZ, xyz_2 : XYZ):
    # calculates the distance between 2 XYZs
    return math.sqrt((pow(xyz_1.x - xyz_2.x, 2.0)) + (pow(xyz_1.y - xyz_2.y, 2.0)) + (pow(xyz_1.z - xyz_2.z, 2.0)))

async def is_free(client: Client):
	# Returns True if not in combat, loading screen, or in dialogue.
	return not any([await client.is_loading(), await client.in_battle()])

async def is_in_loading(client: Client):
	# Returns True if not in combat, loading screen, or in dialogue.
	return not any([await client.is_loading()])

async def is_in_combat(client: Client):
	# Returns True if not in combat, loading screen, or in dialogue.
	return not any([await client.in_battle()])

async def wait_for_free(client: Client, wait_for_not: bool = False, interval: float = 0.25):
    if wait_for_not:
        while await is_free(client):
            await asyncio.sleep(interval)

    else:
        while not await is_free(client):
            await asyncio.sleep(interval)

async def wait_for_loading(client: Client, wait_for_not: bool = False, interval: float = 0.25):
    if wait_for_not:
        while await is_in_loading(client):
            await asyncio.sleep(interval)

    else:
        while not await is_in_loading(client):
            await asyncio.sleep(interval)

async def wait_for_combat(client: Client, wait_for_not: bool = False, interval: float = 0.25):
    if wait_for_not:
        while await is_in_combat(client):
            await asyncio.sleep(interval)

    else:
        while not await is_in_combat(client):
            await asyncio.sleep(interval)

async def set_player_scale(scale_to_set, client: Client, default_scale: float = 1.0):
    scale = await client.body.scale()
    if scale:
        await client.body.write_scale(scale_to_set)
    else:
        await client.body.write_scale(default_scale)
        await set_player_scale(scale_to_set, client)
        await asyncio.sleep(1)
    # await client.send_key(Keycode.W, 0.1)

async def set_player_speed(speed_to_set, client: Client, default_speed: int = 1):
    speed = await client.client_object.speed_multiplier()
    if speed:
        # print("Set speed!")
        await client.client_object.write_speed_multiplier(speed_to_set)
    else:
        # print("Speed wasn't found for some reason? Trying again...")
        await client.client_object.write_speed_multiplier(default_speed)
        await set_player_speed(speed_to_set, client)
        await asyncio.sleep(1)

async def set_camera_distance(min, max, set, zoom, client: Client, default_distance: float = 300.0):
    camera: ElasticCameraController = await client.game_client.elastic_camera_controller()
    client_object = await client.body.parent_client_object()
    await camera.write_attached_client_object(client_object)
    if set and min and max:
        await camera.write_distance_target(set)
        await camera.write_distance(set)
        await camera.write_min_distance(min)
        await camera.write_max_distance(max)
        if zoom:
            await camera.write_zoom_resolution(zoom)
    else:
        await camera.write_distance_target(default_distance)
        await camera.write_distance(default_distance)
        await camera.write_min_distance(150.0)
        await camera.write_max_distance(450.0)

async def update_camera(pitch, roll, yaw, camera: CameraController):
    camera_rot = await camera.orientation()
    if camera_rot:
        if pitch == None:
            pitch = camera_rot.pitch
        if roll == None:
            roll = camera_rot.roll
        if yaw == None:
            yaw = camera_rot.yaw
        await camera.update_orientation(Orient(pitch, roll, yaw))

async def update_player(pitch, roll, yaw, client: Client):
    player_rot = await client.body.orientation()
    if player_rot:
        if pitch == None:
            pitch = player_rot.pitch
        if roll == None:
            roll = player_rot.roll
        if yaw == None:
            yaw = player_rot.yaw
        await client.body.write_orientation(Orient(pitch, roll, yaw))

async def unhook_ww(client: Client, client_camera: CameraController, handler: ClientHandler):
    if not client == False:
        print(Back.RED + Fore.WHITE + "Resetting Character..." + Back.RESET)
        try:
            await set_player_scale(1.0, client)
            print("Scale Reset.")
        except Exception as e:
            print(f"Failed to reset scale: {e}")
        try:
            await set_player_speed(0, client)
            print("Speed Reset.")
        except Exception as e:
            print(f"Failed to reset scale: {e}")
        print(Back.RED + Fore.WHITE + "Unhooking Mod..." + Back.RESET)
        try:
            await handler.close()
            client = False
            print("Mod Unhooked.")
        except Exception as e:
            print(f"Failed to reset scale: {e}")
    else:
        print("")

client = False
camera = False
handler = False
async def start():
    global client
    global camera
    global handler
    print("\nTap's Speedrun Challenge:")
    try:
        handler = ClientHandler()
        print(Fore.BLUE + "HOOKING | " +
    Fore.WHITE + "Detecting Wizard101...")
        print(Fore.BLUE + "HOOKING | " +
    Fore.WHITE + "Initializing client...")
        client = handler.get_new_clients()[0]
        print(Fore.BLUE + "HOOKING | " +
    Fore.WHITE + "Client found!")
        client_camera = await client.game_client.selected_camera_controller()
        try:
            print(Fore.BLUE + "HOOKING | " +
    Fore.WHITE + "Hooking clients...")
            print(Style.DIM + f"(If nothing happens after a few seconds make sure you're IN THE GAME, not in the wizard selection.)" + Style.RESET_ALL)
            await client.activate_hooks()
            print(Fore.BLUE + "HOOKING | " +
    Fore.GREEN + "Hooked!")

            input(Fore.BLUE + "LAUNCHING | " + Fore.GREEN + "Press ENTER to start 3 second countdown.")
            print(Fore.BLUE + "LAUNCHING | " + Fore.GREEN + "3" + Style.DIM  + Fore.WHITE + " 2 1" + Style.RESET_ALL, end="", flush=True)
            await asyncio.sleep(1)
            print('\b' * len("LAUNCHING | 3 2 1"), end='', flush=True)
            print(Fore.BLUE + "LAUNCHING | " + Style.DIM + Fore.WHITE + "3" + Style.RESET_ALL + Fore.GREEN + " 2 " + Style.DIM + Fore.WHITE + "1" + Style.RESET_ALL, end="", flush=True)
            await asyncio.sleep(1)
            print('\b' * len("LAUNCHING | 3 2 1"), end='', flush=True)
            print(Fore.BLUE + "LAUNCHING | " + Style.DIM + Fore.WHITE + "3 2 " + Style.RESET_ALL + Fore.GREEN + "1" + Fore.WHITE, end="", flush=True)
            await asyncio.sleep(1)
            print('\b' * len("LAUNCHING | 3 2 1"), end='', flush=True)
            
            print(Fore.YELLOW + f'Starting scripts... \nPress CTRL+C to close script COMPLETELY. ' + Style.DIM + f'(otherwise you have to restart Wizard101 when re-running.)\n' + Style.RESET_ALL)
            tasks = [boost(client, client_camera, handler), grow(client, client_camera, handler), npc(client, client_camera, handler), load_check(client, client_camera, handler)]
            try:
                await asyncio.gather(*tasks)
                await unhook_ww(client, client_camera, handler)
                input(Style.DIM + "Press ENTER to close this terminal." + Style.RESET_ALL)
            except Exception as e:
                input(f'{e}\n\nPress ENTER to close terminal.')
                # try:
                #     await unhook_ww(client, client_camera, handler)
                # except Exception as e:
                #     print(f"{e}")
                # input(Style.DIM + "Press ENTER to close this terminal." + Style.RESET_ALL)

        except Exception as e:
            await unhook_ww(client, client_camera, handler)
            print(Fore.RED + "ERR | " +
    Fore.RED + "An error occured while hooking clients: " + Fore.WHITE + f' {e}')
            input(Style.DIM + "Press ENTER to close this terminal." + Style.RESET_ALL)

    except Exception as e:
        if 'root.wad not found' in f'{e}':
            print(Fore.RED + "\nInvalid Wizard101 file path.\n" + Fore.RESET + f"{Fore.YELLOW} 1. {Fore.WHITE}Right click your {Fore.GREEN}Wizard101 icon.{Fore.WHITE} \n{Fore.YELLOW} 2. {Fore.WHITE}Click {Fore.GREEN}properties. {Fore.WHITE}\n{Fore.YELLOW} 3. {Fore.WHITE}Copy the text in the {Fore.GREEN}Start in:{Fore.WHITE} box {Fore.GREEN}without the quotation marks. {Fore.WHITE}\n{Fore.YELLOW} 4. {Fore.WHITE}That's your Wizard101 path!\n{Style.DIM}Should look something like: {Style.RESET_ALL}E:\Kingsisle Entertainment\Wizard101")
        elif 'out of range' in f'{e}':
            print(Fore.RED + "Wizard101 is not open, please open wizard101 before starting the mod." + Fore.RESET + Style.DIM + f' ({e})' + Style.RESET_ALL)
        else: 
            print(Fore.RED + "An error occured, try opening or restarting Wizard101." + Fore.RESET + Style.DIM + f' ({e})' + Style.RESET_ALL)

        try:
            await unhook_ww(client, client_camera, handler)
        except:
            print("")
        input(Style.DIM + "Press ENTER to close this terminal." + Style.RESET_ALL)

async def boost(client: Client, camera: CameraController, handler: ClientHandler):
    try:
        if client:
            print(Fore.CYAN + "Initializing | " +
        Fore.GREEN + f"Random speed every 10 seconds.")
            print(Fore.YELLOW + "Initialized | " +
        Fore.GREEN + f"Random speed loop started." + Fore.WHITE)
            while True: # Begin loop
                await asyncio.sleep(10) # wait 10 seconds
                random_number = 0
                sign = random.choice([-1, 1])
                if sign == -1:
                    random_number = random.randint(-80, 0)
                else:
                    random_number = random.randint(0, 10000)
                print(Fore.BLUE + "New Speed: " +
        Fore.LIGHTGREEN_EX + f"{random_number}%" + Fore.WHITE)
                await set_player_speed(random_number, client)
        else: 
            print(Fore.RED + "Client was never initiated." + Fore.RESET)
    except:
        print(Fore.RED + "Speed function disabled." + Fore.RESET)
        await asyncio.sleep(1)
        await unhook_ww(client, camera, handler)

async def grow(client: Client, camera: CameraController, handler: ClientHandler):
    try:
        if client:
            print(Fore.CYAN + "Initializing | " +
            Fore.GREEN + f"Grow player size 0.1% every second.")
            player_size = 1
            print(Fore.YELLOW + "Initialized | " +
        Fore.GREEN + f"Player now growing." + Fore.WHITE)
            while True: # Begin loop
                player_size += 0.001
                await set_player_scale(player_size, client)
                await asyncio.sleep(1)
        else: 
            print(Fore.RED + "Client was never initiated." + Fore.RESET)
    except:
        print(Fore.RED + "Size function disabled." + Fore.RESET)
        await asyncio.sleep(2)
        await unhook_ww(client, camera, handler)

async def npc(client: Client, camera: CameraController, handler: ClientHandler):
    try:
        if client:
            print(Fore.CYAN + "Initializing | " +
            Fore.GREEN + f"After every fight, tp to a random mob/npc.")
            entity_list = []
            print(Fore.YELLOW + "Initialized | " +
        Fore.GREEN + f"Combat detector enabled." + Fore.WHITE)
            while True: # Begin loop
                await wait_for_combat(client, True) # Waiting for wizard to join a fight.
                await wait_for_combat(client) # Once in a fight, wait for fight to finish.

                # Then tp to random entity:
                ent_list = await client.get_base_entity_list()
                try:
                    for entity in ent_list:
                        if await entity.display_name():
                            if calc_Distance(await client.body.position(), await entity.location()) < 25000:
                                entity_list.append(entity)
                    chosen_entity = random.choice(entity_list)
                    await client.teleport(await chosen_entity.location())
                    print(Fore.CYAN + f"FIGHT COMPLETED |" + Fore.LIGHTGREEN_EX +  f" Teleported to" + Fore.BLUE + f" {await chosen_entity.display_name()}." + Fore.RESET)
                except:           
                    print(Fore.CYAN + f"FIGHT COMPLETED |" + Fore.RED + f" No entity found." + Fore.RESET)
                entity_list = [] # Reset entity list.
        else: 
            print(Fore.RED + "Client was never initiated." + Fore.RESET)
    except:
        print(Fore.RED + "Random TP function disabled." + Fore.RESET)
        await asyncio.sleep(3)
        await unhook_ww(client, camera, handler)

async def load_check(client: Client, camera: CameraController, handler: ClientHandler):
    try:
        if client:
            print(Fore.CYAN + "Initializing | " +
                  Fore.GREEN + f"Load detection.")
            print(Fore.YELLOW + "Initialized | " +
                  Fore.GREEN + f"Reapplying size and speed on load.\n" + Fore.WHITE)
            while True:
                try:
                    await wait_for_loading(client, True)  # Waiting for wizard to see a loading screen.
                    await wait_for_loading(client)  # Once in a fight, wait for loading to finish.
                    player_size = await client.body.scale()
                    player_speed = await client.client_object.speed_multiplier()
                    print(Fore.CYAN + "Detected zone change, reapplying size/speed..." + Fore.RESET)
                    await asyncio.sleep(0.25)  # increase if you load slower

                    async def reapply_effects():
                        try:
                            await set_player_scale(player_size, client)
                            await set_player_speed(player_speed, client)
                            print(Fore.CYAN + f"SIZE: {player_size}x, SPEED: {player_speed}%.")
                        except Exception as e:
                            print(Fore.RED + "Failed to re-apply size and speed, trying again..." + Fore.RESET)
                            await asyncio.sleep(0.1)
                            await reapply_effects()
                            print(f'{e}')

                    await reapply_effects()
                except asyncio.CancelledError:
                    print(Fore.RED + "Load detection cancelled." + Fore.RESET)
                    break
                except Exception as e:
                    print(Fore.RED + "Load detection error." + Fore.RESET)
                    await unhook_ww(client, camera, handler)
                    print(f'{e}')
        else:
            print(Fore.RED + "Client was never initiated." + Fore.RESET)
    except KeyboardInterrupt:
        pass
# This function checks if you encounter a loading screen (or enter a new zone, which clears all effects)

        
if __name__ == "__main__":
    try:
        asyncio.run(start())
    except Exception as error:
        print(Fore.RED + f"{error}" + Fore.RESET)
        pass
