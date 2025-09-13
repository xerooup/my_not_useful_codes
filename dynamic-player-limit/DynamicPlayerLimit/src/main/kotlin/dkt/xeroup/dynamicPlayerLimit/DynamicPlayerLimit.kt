package dkt.xeroup.dynamicPlayerLimit

import org.bukkit.Bukkit
import org.bukkit.event.EventHandler
import org.bukkit.event.Listener
import org.bukkit.event.player.PlayerJoinEvent
import org.bukkit.event.player.PlayerQuitEvent
import org.bukkit.plugin.java.JavaPlugin
import org.bukkit.scheduler.BukkitTask
import java.util.concurrent.atomic.AtomicReference

class DynamicPlayerLimit : JavaPlugin() {
    private val listener = Listen(this)
    override fun onEnable() {
        server.pluginManager.registerEvents(listener, this)
        listener.updatePlayerLimit()
        logger.info("Plugin DynamicPlayerLimit is enabled!")
    }
}

class Listen(private val plugin: JavaPlugin) : Listener {
    private val updateTaskRef = AtomicReference<BukkitTask?>(null)

    @EventHandler
    fun onPlayerJoin(event: PlayerJoinEvent) {
        scheduleUpdate()
    }

    @EventHandler
    fun onPlayerQuit(event: PlayerQuitEvent) {
        scheduleUpdate()
    }

    private fun scheduleUpdate() {
        updateTaskRef.get()?.cancel()

        val newTask = Bukkit.getScheduler().runTaskLater(plugin, Runnable {
            updatePlayerLimit()
            updateTaskRef.set(null)
        }, 5L)

        updateTaskRef.set(newTask)
    }

    fun updatePlayerLimit() {
        val currentPlayers = Bukkit.getOnlinePlayers().size
        val newLimit = if (currentPlayers == 0) 1 else currentPlayers + 1
        Bukkit.getServer().setMaxPlayers(newLimit)
    }
}